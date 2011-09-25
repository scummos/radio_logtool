import ossaudiodev
import wave
import sys
from struct import unpack, pack
from array import array
from numpy import array as narray
from time import time, sleep
from math import floor
import mainwindow

from PyQt4.QtGui import QMainWindow, QApplication, QColor
from PyQt4.QtCore import QThread, QTimer, QMutex
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
    newData = array('L', [])
    for rangeBegin in range(0, len(data), samples):
        newData.append(sum([x**2 for x in data[rangeBegin:rangeBegin+samples]]))
    return newData

def addRegisteredBlocks(blocks):
    return sum([narray(block)**2 for block in blocks])

def writeArrayToDatafile(data, filename):
    print "Writing datafile %s" % filename
    with open(filename, 'w') as fileptr:
        for item in data:
            fileptr.write(str(item) + "\n")

class Recorder(QThread):
    def __init__(self, length):
        super(Recorder, self).__init__()
        self.chunkSize = 1024
        self.format = ossaudiodev.AFMT_S16_LE
        self.channels = 1
        self.rate = SAMPLE_RATE
        self.length = length
        self.data = ""
        self.stream = ossaudiodev.open('r')
        self.stream.setfmt(self.format)
        self.stream.speed(self.rate)
    
    def cleanup(self):
        self.data = ""
    
    def finalize(self):
        self.data = ""
        self.stream.close()
    
    def run(self):
        """Record a chunk of "length" seconds, and return it as int array"""
        length = self.length
        print "Recording block of length", length
        self.data = self.stream.read(int(length * self.rate + 1) * 2) # 1*2 = sizeof(short)
        return
    
    def __del__(self):
        self.stream.close()

def verify(conversionResult, defaultValue = 0, error = False, parent = False):
    if conversionResult[1]:
        return conversionResult[0]
    if parent and error:
        parent.ui.statusbar.message("Invalid value for %s, defaulting to %s" % (error, defaultValue))
    return defaultValue

class DataProcessor(QThread):
    def run(self):
        t0 = time()
        if self.mode == 'unpack_and_integrate':
            try:
                self.data = unpackData(self.data)
                self.integrationInterval = 1 if self.integrationInterval < 1 else self.integrationInterval
                self.data = integrateData(self.data, self.integrationInterval)
                if self.save:
                    writeArrayToDatafile(self.data, self.filename)
            except OverflowError:
                print "!! overflow while processing data, not saving"
                self.data = False
        if self.mode == 'partition_and_add':
            self.data = addRegisteredBlocks(self.data)
            if self.save:
                writeArrayToDatafile(self.data, self.filename)
        print "Time taken for data processing:", time() - t0

class PreviewGenerator(QThread):
    def __init__(self):
        super(PreviewGenerator, self).__init__()
        self.plotobject = False
        self.plotobjects = []
        
    def run(self):
        t0 = time()
        index = 0
        self.plotobject = KPlotObject(self.color, KPlotObject.Lines, 1)
        for point in self.data:
            self.plotobject.addPoint(index, point)
            index += 1
        self.bounds = (0, len(self.data), min(self.data), max(self.data))
        self.plotobjects.append(self.plotobject)
        if len(self.plotobjects) > 3:
            self.plotobjects.pop()
        if len(self.widget.plotObjects()):
            self.widget.replacePlotObject(0, self.plotobject)
        else:
            self.widget.addPlotObject(self.plotobject)
        self.widget.setLimits(*self.bounds)
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
        self.ui.mode_group.clicked.connect(self.toggleOperationMode)
        self.ui.mode_group.toggled.connect(self.toggleDataAcquisition)
        self.toggleOperationMode()
        self.dataQueue = False
        self.startRecording()
        self.previewTimer = QTimer()
        self.previewTimer.setInterval(verify(self.ui.preview_repeatInterval.text().toFloat(), 2.0, "preview interval", self) * 1000)
        self.previewTimer.timeout.connect(self.refreshPreview)
        self.previewTimer.start()
        self.resultRegnerationTimer = QTimer()
        self.resultRegnerationTimer.setInterval(verify(self.ui.preview_repeatInterval.text().toFloat(), 2.0, "preview interval", self) * 5000)
        self.resultRegnerationTimer.timeout.connect(self.regenerateAndDisplayResult)
        self.resultRegnerationTimer.start()
        self.ui.control_clear.clicked.connect(self.clearData)
        self.chunkIndex = 0
        self.dataAccessMutex = QMutex()
        self.dataProcessor = DataProcessor()
        self.currentPreviewGenerator = PreviewGenerator()
        self.totalPreviewGenerator = PreviewGenerator()
        self.resultRegenerationWorker = DataProcessor()
        self.data = []
        self.abortRecording = False
    
    def toggleDataAcquisition(self):
        if not self.ui.mode_group.isChecked():
            self.abortRecording = True
        elif self.abortRecording:
                self.startRecording()
                self.abortRecording = False
    
    def clearData(self):
        self.data = []
        self.ui.plot_current.resetPlot()
        self.ui.plot_sum.resetPlot()
    
    def toggleOperationMode(self):
        print "setting new operation mode:",
        if self.ui.mode_gradient.isChecked():
            self.mode = 'gradient'
        else:
            self.mode = 'interval'
        print self.mode
    
    def toggleAutoUpdate(self):
        if self.ui.preview_group.isChecked():
            if not self.previewTimer.isActive():
                self.updateRecordingInterval()
                self.previewTimer.start()
                self.resultRegnerationTimer.start()
        else:
            if self.previewTimer.isActive():
                self.previewTimer.stop()
                self.resultRegnerationTimer.stop()
    
    def length(self):
        return verify(self.ui.intervalSettings_length.text().toFloat(), 0.5, "recording interval", self)
    
    def integrationInterval(self):
        return verify(self.ui.intervalSettings_integrate.text().toInt(), 1, "integration interval", self)
    
    def updateRecordingInterval(self):
        self.recorderThread.length = self.length()
    
    def regenerateAndDisplayResult(self):
        if not self.resultRegenerationWorker.isRunning():
            self.resultRegenerationWorker.mode = 'partition_and_add'
            self.resultRegenerationWorker.integrationInterval = self.integrationInterval()
            self.resultRegenerationWorker.length = self.length()
            targetPath = self.targetPath()
            if targetPath:
                self.resultRegenerationWorker.filename = targetPath + "result"
                self.resultRegenerationWorker.save = self.ui.record_startstop.isChecked()
            else:
                self.resultRegenerationWorker.save = False
            self.dataAccessMutex.lock()
            self.resultRegenerationWorker.data = self.data
            self.dataAccessMutex.unlock()
            self.resultRegenerationWorker.start()
            self.resultRegenerationWorker.finished.connect(self.displayResult)
    
    def displayResult(self):
        if not self.totalPreviewGenerator.isRunning() and len(self.data):
            self.dataAccessMutex.lock()
            self.totalPreviewGenerator.data = self.resultRegenerationWorker.data
            self.totalPreviewGenerator.color = QColor(255, 200, 44)
            self.dataAccessMutex.unlock()
            self.totalPreviewGenerator.widget = self.ui.plot_sum
            self.totalPreviewGenerator.start()
    
    def startRecording(self):
        self.recorderThread = Recorder(self.length())
        self.recorderThread.start(QThread.TimeCriticalPriority)
        self.recorderThread.finished.connect(self.handleRecordFinished)
    
    def refreshPreview(self):
        if not self.currentPreviewGenerator.isRunning() and len(self.data):
            self.dataAccessMutex.lock()
            self.currentPreviewGenerator.data = self.data[-1]
            self.dataAccessMutex.unlock()
            self.currentPreviewGenerator.widget = self.ui.plot_current
            self.currentPreviewGenerator.color = QColor(61, 204, 255)
            self.currentPreviewGenerator.start()
    
    def handleProcessedData(self):
        self.dataAccessMutex.lock()
        if self.dataProcessor.data:
            self.data.append(self.dataProcessor.data)
        self.dataAccessMutex.unlock()
    
    def targetPath(self):
        url = self.ui.record_url.url()
        targetPath = False
        if url.isValid():
            targetPath = url.path() + "/" + self.ui.record_prefix.text()
        return targetPath
        
    
    def handleQueuedData(self):
        self.dataAccessMutex.lock()
        self.dataProcessor.data = self.dataQueue
        self.dataAccessMutex.unlock()
        self.dataProcessor.mode = 'unpack_and_integrate'
        self.dataProcessor.integrationInterval = self.integrationInterval()
        targetPath = self.targetPath()
        if targetPath:
            filenameForChunk = targetPath + "%04i" % self.chunkIndex
            self.dataProcessor.save = self.ui.record_startstop.isChecked()
            self.dataProcessor.filename = filenameForChunk
            if self.dataProcessor.save:
                self.mainwin.ui.statusbar.message("About to write datafile \"%s\"" % filenameForChunk)
                self.chunkIndex += 1
        else:
            self.dataProcessor.save = False
            self.ui.statusbar.message("Invalid save file path, not saving data!")
        self.dataProcessor.finished.connect(self.handleProcessedData)
        self.dataProcessor.start()
    
    def handleRecordFinished(self):
        data = self.recorderThread.data
        
        if not self.abortRecording:
            self.recorderThread.cleanup()
            self.recorderThread.start(QThread.TimeCriticalPriority)
        else:
            self.recorderThread.finalize()
        
        self.dataAccessMutex.lock()
        self.dataQueue = data
        self.dataAccessMutex.unlock()
        self.handleQueuedData()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = mainwin()
    w.show()
    sys.exit(app.exec_())
