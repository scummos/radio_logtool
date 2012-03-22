import ossaudiodev
import wave
import sys
from struct import unpack, pack
from array import array
from numpy import array as narray, median
from time import time, sleep
from math import floor
import mainwindow
import copy

from PyQt4.QtGui import QMainWindow, QApplication, QColor
from PyQt4.QtCore import QThread, QTimer, QMutex, pyqtSignal
from PyKDE4.kio import KFile
from PyKDE4.kdeui import KPlotWidget, KPlotObject

SAMPLE_RATE = 44100

def unpackData(data):
    return unpack('<' + ('h'*(len(data)/2)), data)

def partitionData(data, length, integrationInterval = 1):
    blockSize = int(SAMPLE_RATE * length / integrationInterval)
    print "Partitioning data into blocks of", blockSize, "frames"
    size = len(data)
    atFrame = 0
    blocks = []
    while atFrame + blockSize <= size:
        blocks.append(data[atFrame:atFrame+blockSize])
        atFrame += blockSize
    return blocks

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
    print m, h, sn
    return sn < 300

def writeArrayToDatafile(data, filename):
    print "Writing datafile %s" % filename
    with open(filename, 'w') as fileptr:
        for item in data:
            fileptr.write(str(item) + "\n")

class Recorder(QThread):
    dataAvailable = pyqtSignal()
    
    def __init__(self, length):
        super(Recorder, self).__init__()
        self.chunkSize = 1024
        self.format = ossaudiodev.AFMT_S16_LE
        self.channels = 1
        self.rate = SAMPLE_RATE
        self.length = length
        self.data = []
        self.stream = ossaudiodev.open('r')
        self.stream.setfmt(self.format)
        self.stream.speed(self.rate)
        self.stop = False
        self.dataAccessMutex = QMutex()
    
    def cleanup(self):
        self.dataAccessMutex.lock()
        self.data = []
        self.dataAccessMutex.unlock()
    
    def finalize(self):
        self.cleanup()
        self.stream.close()
    
    def run(self):
        """Record a chunk of "length" seconds, and return it as int array"""
        self.stop = False
        while not self.stop:
            length = self.length
            print "Recording block of length", length
            newData = self.stream.read(int(length * self.rate + 1) * 2)
            self.dataAccessMutex.lock()
            self.data.append(newData) # 1*2 = sizeof(short)
            self.dataAccessMutex.unlock()
            self.dataAvailable.emit()
        self.finalize()
        return
    
    def __del__(self):
        self.stream.close()

def verify(conversionResult, defaultValue = 0, error = False, parent = False):
    if conversionResult[1]:
        return conversionResult[0]
    if parent and error:
        parent.ui.statusbar.message("Invalid value for %s, defaulting to %s" % (error, defaultValue))
    return defaultValue

class PreviewGenerator():
    def __init__(self):
        self.plotobject = False
        self.plotobjects = []
        
    def run(self):
        if self.data is False:
            return
        t0 = time()
        index = 0
        self.plotobject = KPlotObject(self.color, KPlotObject.Lines, 1)
        for point in self.data:
            self.plotobject.addPoint(index, point)
            index += 1
            if index % 20 == 0:
                QApplication.processEvents()
        self.bounds = (0, len(self.data), min(self.data), max(self.data))
        self.plotobjects.append(self.plotobject)
        if len(self.plotobjects) > 3:
            self.plotobjects.pop()
        self.widget.setLimits(*self.bounds)
        if len(self.widget.plotObjects()):
            self.widget.replacePlotObject(0, self.plotobject)
        else:
            self.widget.addPlotObject(self.plotobject)
        print "Time taken for preview generation:", time() - t0

class mainwin(QMainWindow):
    def __init__(self):
        super(mainwin, self).__init__()
        self.ui = mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.record_url.setMode(KFile.Directory)
        self.ui.gradientSettings_group.setVisible(False)
        self.ui.window_splitter.setSizes([600, 200])
        self.ui.intervalSettings_length.textChanged.connect(self.updateRecordingInterval)
        self.ui.preview_group.toggled.connect(self.toggleAutoUpdate)
        self.ui.preview_now.clicked.connect(self.refreshPreview)
        self.abortRecording = False
        self.ui.mode_group.clicked.connect(self.toggleDataAcquisitionAndOperationMode)
        self.ui.mode_gradient.toggled.connect(self.toggleDataAcquisitionAndOperationMode)
        self.ui.mode_interval.toggled.connect(self.toggleDataAcquisitionAndOperationMode)
        self.mode = None
        self.dataAccessMutex = QMutex()
        self.dataQueue = False
        self.startRecording()
        self.previewTimer = QTimer()
        self.resultRegenerationTimer = QTimer()
        self.updatePreviewIntervals()
        self.previewTimer.timeout.connect(self.refreshPreview)
        self.previewTimer.start()
        self.resultRegenerationTimer.timeout.connect(self.regenerateAndDisplayResult)
        self.resultRegenerationTimer.start()
        self.ui.preview_repeatInterval.textChanged.connect(self.updatePreviewIntervals)
        self.ui.control_clear.clicked.connect(self.clearData)
        self.toggleDataAcquisitionAndOperationMode()
        self.chunkIndex = 0
        self.currentPreviewGenerator = PreviewGenerator()
        self.totalPreviewGenerator = PreviewGenerator()
        self.data = []
        self.isFirstChunk = True
    
    def updatePreviewIntervals(self):
        self.previewTimer.setInterval(verify(self.ui.preview_repeatInterval.text().toFloat(), 2.0, "preview interval", self) * 1000)
        if self.mode == 'gradient':
            multiplier = 1
        else:
            multiplier = 5
        self.resultRegenerationTimer.setInterval(verify(self.ui.preview_repeatInterval.text().toFloat(), 2.0, "preview interval", self) * 1000 * multiplier)
    
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
            if not self.previewTimer.isActive():
                self.updateRecordingInterval()
                self.previewTimer.start()
                self.resultRegenerationTimer.start()
        else:
            if self.previewTimer.isActive():
                self.previewTimer.stop()
                self.resultRegenerationTimer.stop()
    
    def length(self):
        if self.mode == 'interval':
            return verify(self.ui.intervalSettings_length.text().toFloat(), 0.5, "recording interval", self)
        else:
            return verify(self.ui.gradientSettings_integrate.text().toFloat(), 1.0, "integration interval", self)
    
    def integrationInterval(self):
        return verify(self.ui.intervalSettings_integrate.text().toInt(), 1, "integration interval", self)
    
    def updateRecordingInterval(self):
        self.recorderThread.length = self.length()
        self.clearData()
    
    def regenerateAndDisplayResult(self):
        targetPath = self.targetPath()
        if targetPath:
            filename = targetPath + "result"
            save = self.ui.record_startstop.isChecked()
        else:
            save = False
        
        self.dataAccessMutex.lock()
        if self.mode == 'interval':
            print "Using interval method"
            summarizedData = addRegisteredBlocks(self.data)
        if self.mode == 'gradient':
            print "Using gradient method"
            summarizedData = self.data
        self.dataAccessMutex.unlock()
        if save:
            writeArrayToDatafile(summarizedData, filename)
        self.displayResult(summarizedData)
    
    def displayResult(self, data):
        self.totalPreviewGenerator.data = data
        self.totalPreviewGenerator.color = QColor(255, 200, 44)
        self.totalPreviewGenerator.widget = self.ui.plot_sum
        self.totalPreviewGenerator.run()
    
    def startRecording(self):
        self.recorderThread = Recorder(self.length())
        self.recorderThread.dataAvailable.connect(self.handleRecordFinished)
        self.recorderThread.start(QThread.TimeCriticalPriority)
    
    def refreshPreview(self):
        self.dataAccessMutex.lock()
        if self.previousChunk:
            self.currentPreviewGenerator.data = copy.deepcopy(self.previousChunk)
            self.currentPreviewGenerator.widget = self.ui.plot_current
            self.currentPreviewGenerator.color = QColor(61, 204, 255)
            self.currentPreviewGenerator.run()
        self.dataAccessMutex.unlock()
    
    def targetPath(self):
        url = self.ui.record_url.url()
        targetPath = False
        if url.isValid():
            targetPath = url.path() + "/" + self.ui.record_prefix.text()
        return targetPath
    
    def handleQueuedData(self):
        self.dataAccessMutex.lock()
        data = self.dataQueue
        targetPath = self.targetPath()
        if targetPath:
            filenameForChunk = targetPath + "%04i" % self.chunkIndex
            save = self.ui.record_startstop.isChecked()
            if save:
                self.ui.statusbar.message("About to write datafile \"%s\"" % filenameForChunk)
                self.chunkIndex += 1
        else:
            save = False
            self.ui.statusbar.message("Invalid save file path, not saving data!")
        try:
            data = unpackData(data)
            self.dataAccessMutex.unlock()
            data = integrateData(data, self.integrationInterval())
            if not checkData(data):
                print "Data seems corrupted. skipping"
                return  
            if save:
                writeArrayToDatafile(data, filenameForChunk)
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
