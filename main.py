import sys
from struct import unpack, pack
from array import array
from numpy import array as narray, median
from time import time, sleep
from math import floor
import mainwindow
import copy

from datetime import datetime

from PyQt4.QtGui import QMainWindow, QApplication, QColor, QPen
from PyQt4.QtCore import QThread, QTimer, QMutex, pyqtSignal
from PyQt4 import QtGui, QtCore
from PyKDE4.kio import KFile, KFileDialog
from PyKDE4.kdeui import KPlotWidget, KPlotObject, KMessageBox
from PyKDE4 import kdecore

from i2c import mcp3426Client as connection, ds1629Client as temperatureConnection

from collections import namedtuple

samplesPerSecond = 15

def integrateData(data, samples):
    newData = array('f', [])
    for rangeBegin in range(0, len(data), samples):
        newData.append(sum([x**2 for x in data[rangeBegin:rangeBegin+samples]]))
    return newData

def addRegisteredBlocks(blocks):
    to = time()
    result = sum([narray(block)**2 for block in blocks])
    print "Time needed for adding blocks:", time() - to
    return result

def checkData(data):
    m = median(data)
    h = max(data)
    sn = float(h)/m
    return sn < 300

def writeArrayToDatafile(data, filename):
    print "Writing datafile %s" % filename
    with open(filename, 'w') as fileptr:
        for item in data:
            fileptr.write(str(item) + "\n")

def appendArrayToDatafile(data, filename):
    #print "Appending datafile %s" % filename
    with open(filename, 'a') as fileptr:
        for item in data:
            fileptr.write(str(item) + "\n")

DataTuple = namedtuple('DataTuple', ['recordingTime', 'data', 'temperature'])

class PrintableDataTuple(DataTuple):
    def __str__(self):
        return ' '.join([str(item) for item in self])

class DelayedFileWriter():
    def __init__(self, file, accum = 480):
        self.data = []
        self.accum = accum
        self.file = file
        
    def write(self, data):
        self.data.append(data)
        self.maybeWriteData()
    
    def doWriteData(self):
        self.maybeWriteData(force = True)
    
    def maybeWriteData(self, force = False):
        if len(self.data) >= self.accum or force:
            with open(self.file, 'a') as fileptr:
                fileptr.write('\n'.join([str(item) for item in self.data]) + "\n")
                self.data = []
    
    def __del__(self):
        self.doWriteData()
        assert self.data == []

class Recorder(QThread):
    dataAvailable = pyqtSignal()
    connectionStatusChanged = pyqtSignal(bool)
    connectionError = pyqtSignal(str)
    operationMode = ("16bit", "1x")
    
    def __init__(self, length):
        super(Recorder, self).__init__()
        self.dataAccessMutex = QMutex()
        self.data = []
        self.client = connection()
        self.temperatureClient = temperatureConnection()
        self.length = length
        self.tempeatureUpdateRequested = False
    
    def requestTemperatureUpdate(self):
        if self.temperatureClient:
            self.tempeatureUpdateRequested = True
    
    def doConnect(self):
        connectionEstablished = False
        try:
            self.client.openDevice()
            self.client.setOperationMode(*self.operationMode)
            self.connectionStatusChanged.emit(True)
            connectionEstablished = True
        except Exception as e:
            self.connectionError.emit(str(e))
            self.connectionStatusChanged.emit(False)
            return connectionEstablished
        try:
            self.temperatureClient.openDevice()
            self.doReadTemperature()
            print "Temperature client initialized successfully."
        except Exception as e:
            self.temperatureClient = None
            print "Temperature client is unavailable: %s." % e
        finally:
            self.client.activate()
        return connectionEstablished
    
    def reconnect(self):
        if self.client.isInitialized():
            try:
                self.client.reinit()
                self.connectionStatusChanged.emit(True)
            except IOError as e:
                self.connectionError.emit(str(e))
                self.connectionStatusChanged.emit(False)
        else:
            self.doConnect()
    
    def cleanup(self):
        self.dataAccessMutex.lock()
        self.data = []
        self.dataAccessMutex.unlock()
    
    def finalize(self):
        self.cleanup()
        del self.client
    
    def doReadTemperature(self):
        # Switch between the i2c clients attached to the board
        if self.temperatureClient is not None:
            self.temperatureClient.activate()
            temperature = self.temperatureClient.readBlock()
            self.client.activate()
            return temperature
        return None
    
    def run(self):
        """Record a chunk of "length" samples, and return it as int array
        Currently length is always 1, but might become relevant for performance later...
        theoretically."""
        self.stop = False
        currentTemperature = None
        while not self.stop:
            #print "Recording block of length", length
            try:
                newData = self.client.readBlock()
                if self.tempeatureUpdateRequested:
                    self.tempeatureUpdateRequested = False
                    currentTemperature = self.doReadTemperature()
            except IOError as e:
                self.connectionStatusChanged.emit(False)
                self.connectionError.emit(str(e))
                return
            
            self.dataAccessMutex.lock()
            self.data.append(PrintableDataTuple("%f" % time(), newData, currentTemperature))
            self.dataAccessMutex.unlock()
            self.dataAvailable.emit()
        self.finalize()
        return

def verify(conversionResult, defaultValue = 0, error = False, parent = False):
    if conversionResult[1]:
        return conversionResult[0]
    if parent and error:
        parent.ui.statusbar.message("Invalid value for %s, defaulting to %s" % (error, defaultValue))
    return defaultValue

class mainwin(QMainWindow):
    def __init__(self):
        super(mainwin, self).__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.record_url.setMode(KFile.Directory)
        self.rawDataFileWriter = None
        self.ui.window_splitter.setSizes([600, 150])
        self.ui.preview_group.toggled.connect(self.toggleAutoUpdate)
        self.abortRecording = False
        self.ui.mode_group.clicked.connect(self.toggleDataAcquisitionAndOperationMode)
        self.ui.mode_gradient.toggled.connect(self.toggleDataAcquisitionAndOperationMode)
        self.ui.mode_interval.toggled.connect(self.toggleDataAcquisitionAndOperationMode)
        self.mode = None
        self.dataAccessMutex = QMutex()
        self.dataQueue = False
        self.startRecording()
        self.updatePreviewIntervals()
        self.ui.preview_repeatInterval.textChanged.connect(self.updatePreviewIntervals)
        self.ui.control_clear.clicked.connect(self.clearData)
        self.toggleDataAcquisitionAndOperationMode()
        self.toggleAutoUpdate()
        self.chunkIndex = 0
        self.data = []
        self.currentDataIndex = 0
        self.currentIntegratedIndex = 0
        self.isFirstChunk = True
        self.ui.actionSave_displayed.activated.connect(self.saveAllData)
        self.ui.gradientSettings_integrate.textChanged.connect(self.updateIntegrationInterval)
        self.ui.record_startstop.toggled.connect(self.updateRecordingState)
        self.ui.record_url.urlSelected.connect(self.updatePath)
        self.ui.record_prefix.textChanged.connect(self.updatePath)
        self.ui.preview_now.clicked.connect(self.redrawPlot)
        self.ui.gradientSettings_group.clicked.connect(self.changeIntegrationMode)
        self.ui.gradientSettings_integrate.textChanged.connect(self.changeIntegrationMode)
        self.changeIntegrationMode()
        self.updateIntegrationInterval()
        self.updateRecordingState()
        self.updatePath()
        self.ui.plot_sum.setAntialiasing(True)
        self.plotobject = None
        self.integratePlotObject = None
        self.ui.actionOpen_and_continue.activated.connect(self.openDataFile)
        
        self.dataAwaitingIntegration = []
        self.invertDataToggled()
        self.ui.invertSignalCheckbox.clicked.connect(self.invertDataToggled)
        
        self.temperatureUpdateTimer = QTimer()
        self.temperatureUpdateTimer.setInterval(1000)
        self.temperatureUpdateTimer.setSingleShot(False)
        self.temperatureUpdateTimer.timeout.connect(self.recorderThread.requestTemperatureUpdate)
        self.temperatureUpdateTimer.start()
        
        self.rawDataBackupCopy = []
    
    def invertDataToggled(self):
        self.invertData = self.ui.invertSignalCheckbox.isChecked()
    
    def verifyDataSaved(self):
        if self.rawDataFileWriter is not None:
            self.rawDataFileWriter.doWriteData()
    
    def changeIntegrationMode(self):
        self.doIntegration = self.ui.gradientSettings_group.isChecked()
        self.integrationInterval = verify(self.ui.gradientSettings_integrate.text().toInt(), 30, "integration interval", self)
        self.recalculateIntegratedData()
    
    def recalculateIntegratedData(self):
        chunkSize = self.integrationInterval
        self.integratedData = []
        for i in xrange(0, len(self.data), chunkSize):
            chunk = self.data[i:i+chunkSize]
            self.integratedData.append(sum(chunk) / float(chunkSize))
    
    def saveAllData(self):
        f = KFileDialog.getSaveFileName()
        try:
            writeArrayToDatafile(self.rawDataBackupCopy, f)
            self.ui.statusbar.message("Successfully saved %s values to %s." % (str(len(self.data)), f))
        except Exception as e:
            self.ui.statusbar.message("Failed to save data to %s: %s" % (f, str(e)))
        
    def updatePath(self):
        self.cachedTargetPath = self.targetPath()
    
    def updateRecordingState(self):
        self.recordingState = self.ui.record_startstop.isChecked()
        self.verifyDataSaved()
    
    def updateIntegrationInterval(self):
        self.integrationInterval = verify(self.ui.gradientSettings_integrate.text().toInt(), 1, "integration interval", self)
        self.integrationInterval = max([self.integrationInterval, 0.04]) # more than 25 updates per second don't make sense
    
    def updatePreviewIntervals(self):
        self.updateInterval = verify(self.ui.preview_repeatInterval.text().toInt(), 4, "preview interval", self)
    
    def toggleDataAcquisitionAndOperationMode(self):
        self.verifyDataSaved()
        if not self.ui.mode_group.isChecked():
            self.abortRecording = True
        elif self.abortRecording:
                self.startRecording()
                self.abortRecording = False
        previousMode = self.mode
        print "setting new operation mode:",
        if self.ui.mode_gradient.isChecked():
            self.mode = 'gradient'
        else:
            self.mode = 'interval'
        print self.mode
        if self.mode != previousMode:
            print "Operation mode changed, clearing data"
            self.clearData()
            self.updatePreviewIntervals()
    
    def indexToTime(self, index):
        return index / (samplesPerSecond * 60.0)
    
    def addIntegratedPoints(self, points):
        for point in points:
            self.integratedRealIndex = self.indexToTime(self.currentIntegratedIndex) * self.integrationInterval
            self.integratePlotObject.addPoint(self.integratedRealIndex, point)
            self.currentIntegratedIndex += 1
    
    def addDataPoint(self, point):
        self.realIndex = self.indexToTime(self.currentDataIndex)
        self.plotobject.addPoint(self.realIndex, point)
        self.currentDataIndex += 1
    
    def openDataFile(self):
        self.verifyDataSaved()
        f = KFileDialog.getOpenFileName()
        s = str(f).split('/')
        self.clearData()
        self.dataAccessMutex.lock()
        try:
            with open(f) as fileptr:
                data = fileptr.readlines()
                self.data = [float(item.split('\t')[1]) for item in data]
            if len(self.data) == 0:
                raise IOError("No valid data points found, probably the file is empty")
            self.ui.record_url.setText('/'.join(s[:-1]))
            self.ui.record_prefix.setText(s[-1].replace('result', '') + "_cont_")
            self.ui.record_startstop.setChecked(False)
            self.updateRecordingState()
            self.ui.statusbar.message("Successfully loaded %s data points from %s." % (len(data), str(f)))
        except Exception as e:
            print e
            try:
                self.ui.statusbar.message("Could not load file %s: %s" % (f, str(e)))
            except:
                self.ui.statusbar.message("Could not load file %s: invalid characters" % f)
        finally:
            if len(self.data) > 0:
                self.addDataPoint(self.data)
            self.redrawPlot()
            self.dataAccessMutex.unlock()
    
    def clearData(self):
        self.verifyDataSaved()
        self.dataAccessMutex.lock()
        self.data = []
        self.integratedData = []
        self.integratedRealIndex = 0
        self.currentIntegratedIndex = 0
        self.dataAwaitingIntegration = []
        self.currentDataIndex = 0
        self.rawDataFileWriter = None
        self.previousChunk = False
        if hasattr(self, "plotobject"):
            self.plotobject.clearPoints()
        if hasattr(self, "integratePlotObject"):
            self.integratePlotObject.clearPoints()
        self.dataAccessMutex.unlock()
    
    def toggleAutoUpdate(self):
        if self.ui.preview_group.isChecked():
            self.updateRecordingInterval()
            self.autoUpdate = True
        else:
            self.autoUpdate = False
    
    def length(self):
        return verify(self.ui.gradientSettings_integrate.text().toInt(), 1, "integration interval", self)
    
    def updateRecordingInterval(self):
        self.recorderThread.length = 1 # TODO make configurable
    
    def connectionStatusChanged(self, isConnected):
        self.deviceConnected = isConnected
        print "Connection status changed:", isConnected
        if isConnected:
            text = '<font style="color:#8BBE00; font-weight:bold">connected</font>'
            self.ui.reconnectButton.setEnabled(False)
            self.ui.statusbar.message("i2c-tiny-usb device connected successfully.")
            self.recorderThread.start()
        else:
            text = '<font style="color:#FF2600; font-weight:bold">not connected</font>'
            self.ui.reconnectButton.setEnabled(True)
        self.ui.connectionStatus.setText("Status: %s" % text)
    
    def IOErrorOccured(self, error):
        self.ui.statusbar.message('Connection error: %s' % error)
    
    def startRecording(self):
        self.recorderThread = Recorder(1)
        self.ui.reconnectButton.setEnabled(True)
        self.recorderThread.dataAvailable.connect(self.handleRecordFinished)
        self.recorderThread.connectionStatusChanged.connect(self.connectionStatusChanged)
        self.recorderThread.connectionError.connect(self.IOErrorOccured)
        self.recorderThread.doConnect()
        if self.deviceConnected:
            self.recorderThread.start(QThread.TimeCriticalPriority)
        self.ui.reconnectButton.clicked.connect(self.recorderThread.reconnect)
    
    def targetPath(self):
        url = self.ui.record_url.url()
        targetPath = False
        if url.isValid():
            targetPath = url.path() + "/" + self.ui.record_prefix.text()
        return targetPath
    
    def handleQueuedData(self):
        self.dataAccessMutex.lock()
        rawData = self.dataQueue
        if self.invertData:
            data = -rawData.data
        else:
            data = rawData.data
        temperature = rawData.temperature
        targetPath = self.cachedTargetPath
        save = self.recordingState
        if save:
            if targetPath:
                filenameForChunk = targetPath + "result"
                self.chunkIndex += 1
            else:
                self.ui.statusbar.message("Invalid save file path, not saving data!")
                save = False
        try:
            if save:
                if self.rawDataFileWriter is None:
                    self.rawDataFileWriter = DelayedFileWriter(filenameForChunk)
                self.rawDataFileWriter.write(rawData)
                time = datetime.now().strftime("%H:%M:%S")
                self.ui.statusbar.message("%s: (delayed) wrote a new value to datafile \"%s\"" % (time, filenameForChunk))
        except OverflowError:
            print "!! overflow while processing data, not saving"
            data = False
        finally:
            self.dataAccessMutex.unlock()
        if data:
            self.previousChunk = data
            self.dataAwaitingIntegration.append(data)
            integratedPointsAdded = self.maybeDoIntegration()
            self.dataAccessMutex.lock()
            self.data.append(data)
            self.rawDataBackupCopy.append(rawData)
            self.dataAccessMutex.unlock()
            
            created = False
            if not self.plotobject:
                created = True
                self.plotobject = KPlotObject(QColor(0, 190, 255), KPlotObject.Lines, 1.0)
            self.addDataPoint(data)
            if created:
                self.ui.plot_sum.addPlotObject(self.plotobject)
            
            created = False
            if not self.integratePlotObject:
                created = True
                # FIXME: the width argument for kplotobject doesn't seem to work...
                self.integratePlotObject = KPlotObject(QColor(0, 0, 0), KPlotObject.Lines, 1.0)
                p = QPen(QColor(200, 200, 255))
                p.setWidth(2.5)
                self.integratePlotObject.setLinePen(p);
            self.addIntegratedPoints(integratedPointsAdded)
            if created:
                self.ui.plot_sum.addPlotObject(self.integratePlotObject)
            
            if (self.currentDataIndex) % self.updateInterval == 0 and self.autoUpdate:
                self.redrawPlot()
            
    
    def maybeDoIntegration(self):
        pointsAdded = []
        while len(self.dataAwaitingIntegration) >= self.integrationInterval:
            integratedValue = sum(self.dataAwaitingIntegration[:self.integrationInterval]) / self.integrationInterval
            self.integratedData.append(integratedValue)
            pointsAdded.append(integratedValue)
            self.dataAwaitingIntegration = self.dataAwaitingIntegration[self.integrationInterval:]
        return pointsAdded
    
    def redrawPlot(self):
        if len(self.data) > 0:
            bounds = (0, self.realIndex*1.05, min(self.data), max(self.data))
            self.ui.plot_sum.setLimits(*bounds)
        self.ui.plot_sum.update()
    
    def handleRecordFinished(self):
        if self.recorderThread.stop:
            return
        
        self.recorderThread.dataAccessMutex.lock()
        data = copy.deepcopy(self.recorderThread.data.pop())
        self.recorderThread.dataAccessMutex.unlock()
        
        if self.abortRecording:
            self.recorderThread.stop = True
        
        if not self.isFirstChunk: # discard the first chunk of data, it's often faulty
            self.dataAccessMutex.lock()
            self.dataQueue = data
            self.dataAccessMutex.unlock()
            self.handleQueuedData()
        else:
            self.isFirstChunk = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = mainwin()
    w.show()
    sys.exit(app.exec_())
