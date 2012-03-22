import sys
from struct import unpack, pack
from array import array
from numpy import array as narray, median
from time import time, sleep
from math import floor
import mainwindow
import copy

from datetime import datetime

from PyQt4.QtGui import QMainWindow, QApplication, QColor
from PyQt4.QtCore import QThread, QTimer, QMutex, pyqtSignal
from PyKDE4.kio import KFile, KFileDialog
from PyKDE4.kdeui import KPlotWidget, KPlotObject
from PyKDE4 import kdecore

from i2c import mcp3426Client as connection

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

class Recorder(QThread):
    dataAvailable = pyqtSignal()
    
    def __init__(self, length):
        super(Recorder, self).__init__()
        self.dataAccessMutex = QMutex()
        self.data = []
        self.client = connection()
        self.client.openDevice()
        self.client.setOperationMode("16bit", "1x")
        self.length = length
    
    def cleanup(self):
        self.dataAccessMutex.lock()
        self.data = []
        self.dataAccessMutex.unlock()
    
    def finalize(self):
        self.cleanup()
        del self.client
    
    def run(self):
        """Record a chunk of "length" samples, and return it as int array"""
        self.stop = False
        while not self.stop:
            #print "Recording block of length", length
            newData = []
            for i in xrange(self.length):
                newData.append(self.client.readBlock())
            self.dataAccessMutex.lock()
            self.data.append(newData) # 1*2 = sizeof(short)
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
        self.resultRegenerationTimer = QTimer()
        self.updatePreviewIntervals()
        self.resultRegenerationTimer.timeout.connect(self.regenerateAndDisplayResult)
        self.resultRegenerationTimer.start()
        self.ui.preview_repeatInterval.textChanged.connect(self.updatePreviewIntervals)
        self.ui.control_clear.clicked.connect(self.clearData)
        self.toggleDataAcquisitionAndOperationMode()
        self.chunkIndex = 0
        self.totalPreviewGenerator = PreviewGenerator(self)
        self.data = []
        self.currentDataIndex = 0
        self.isFirstChunk = True
        self.ui.actionSave_displayed.activated.connect(self.saveAllData)
        self.ui.gradientSettings_integrate.textChanged.connect(self.updateIntegrationInterval)
        self.ui.record_startstop.toggled.connect(self.updateRecordingState)
        self.ui.record_url.urlSelected.connect(self.updatePath)
        self.ui.record_prefix.textChanged.connect(self.updatePath)
        self.updateIntegrationInterval()
        self.updateRecordingState()
        self.updatePath()
        self.ui.plot_sum.setAntialiasing(True)
    
    def saveAllData(self):
        f = KFileDialog.getSaveFileName()
        try:
            writeArrayToDatafile(self.data, f)
            self.ui.statusbar.message("Successfully saved %s values to %s." % (str(len(self.data)), f))
        except Exception as e:
            self.ui.statusbar.message("Failed to save data to %s: %s" % (f, str(e)))
        
    def updatePath(self):
        self.cachedTargetPath = self.targetPath()
    
    def updateRecordingState(self):
        self.recordingState = self.ui.record_startstop.isChecked()
    
    def updateIntegrationInterval(self):
        self.integrationInterval = verify(self.ui.gradientSettings_integrate.text().toInt(), 1, "integration interval", self)
        self.integrationInterval = max([self.integrationInterval, 0.04]) # more than 25 updates per second don't make sense
    
    def updatePreviewIntervals(self):
        self.resultRegenerationTimer.setInterval(verify(self.ui.preview_repeatInterval.text().toFloat(), 2.0, "preview interval", self) * 1000)
    
    def toggleDataAcquisitionAndOperationMode(self):
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
    
    def clearData(self):
        self.dataAccessMutex.lock()
        self.data = []
        self.previousChunk = False
        self.dataAccessMutex.unlock()
    
    def toggleAutoUpdate(self):
        if self.ui.preview_group.isChecked():
            self.updateRecordingInterval()
            self.resultRegenerationTimer.start()
        else:
            self.resultRegenerationTimer.stop()
    
    def length(self):
        return verify(self.ui.gradientSettings_integrate.text().toInt(), 1, "integration interval", self)
    
    def updateRecordingInterval(self):
        self.recorderThread.length = self.length()
        self.clearData()
    
    def regenerateAndDisplayResult(self):
        self.dataAccessMutex.lock()
        data = self.data
        self.dataAccessMutex.unlock()
        integrated = integrateData(data, self.integrationInterval)
        integrated.pop()
        self.displayResult(integrated)
    
    def displayResult(self, data):
        self.totalPreviewGenerator.data = data
        self.totalPreviewGenerator.color = QColor(255, 200, 44)
        self.totalPreviewGenerator.widget = self.ui.plot_sum
        #self.totalPreviewGenerator.run()
    
    def startRecording(self):
        self.recorderThread = Recorder(1)
        self.recorderThread.dataAvailable.connect(self.handleRecordFinished)
        self.recorderThread.start(QThread.TimeCriticalPriority)
    
    def targetPath(self):
        url = self.ui.record_url.url()
        targetPath = False
        if url.isValid():
            targetPath = url.path() + "/" + self.ui.record_prefix.text()
        return targetPath
    
    def handleQueuedData(self):
        self.dataAccessMutex.lock()
        data = self.dataQueue
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
            if not checkData(data):
                print "Data seems corrupted. skipping"
                return  
            if save:
                appendArrayToDatafile(data, filenameForChunk)
                time = datetime.now().strftime("%H:%M:%S")
                self.ui.statusbar.message("%s: wrote %s new values to datafile \"%s\"" % (time, len((data)), filenameForChunk))
        except OverflowError:
            print "!! overflow while processing data, not saving"
            data = False
        finally:
            self.dataAccessMutex.unlock()
        if data:
            self.previousChunk = data
            self.dataAccessMutex.lock()
            if self.mode == 'gradient':
                self.data.append(sum(narray(data)/1.0))
            elif self.mode == 'interval':
                self.data.append(data)
            self.dataAccessMutex.unlock()
            
            existing = self.ui.plot_sum.plotObjects()
            if len(existing) > 0:
                self.plotobject = existing[0]
            else:
                self.plotobject = KPlotObject(QColor(255, 200, 44), KPlotObject.Lines, 1)
            for point in data:
                self.plotobject.addPoint(self.currentDataIndex, point)
                self.currentDataIndex += 1
            bounds = (0, len(self.data), min(self.data), max(self.data))
            self.ui.plot_sum.setLimits(*bounds)
            if len(existing) == 0:
                self.ui.plot_sum.addPlotObject(self.plotobject)
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
