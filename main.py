import ossaudiodev
import wave
import sys
from struct import unpack, pack
from array import array
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
    blockSize = int(self.rate * length / integrationInterval)
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
    result = []
    for frameIndex in range(len(blocks[0])):
        result.append(sum([block[frameIndex] for block in blocks]))
    return result

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
        self.data = unpackData(self.data)
        self.integrationInterval = 1 if self.integrationInterval < 1 else self.integrationInterval
        self.data = integrateData(self.data, self.integrationInterval)
        if self.save:
            writeArrayToDatafile(self.data, self.filename)

class PreviewGenerator(QThread):
    def __init__(self):
        super(PreviewGenerator, self).__init__()
        self.plotobject = False
        self.plotobjects = []
        
    def run(self):
        index = 0
        self.plotobject = KPlotObject(QColor(50, 0, 220), KPlotObject.Lines, 1)
        for point in self.data:
            self.plotobject.addPoint(index, point)
            index += 1
        self.bounds = (0, len(self.data), min(self.data), max(self.data))
        self.plotobjects.append(self.plotobject)
        if len(self.widget.plotObjects()):
            self.widget.replacePlotObject(0, self.plotobject)
        else:
            self.widget.addPlotObject(self.plotobject)
        self.widget.setLimits(*self.bounds)

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
        self.dataQueue = False
        self.startRecording()
        self.previewTimer = QTimer()
        self.previewTimer.setInterval(self.ui.preview_repeatInterval.text().toFloat()[0] * 1000)
        self.previewTimer.timeout.connect(self.refreshPreview)
        self.previewTimer.start()
        self.chunkIndex = 0
        self.dataAccessMutex = QMutex()
        self.dataProcessor = DataProcessor()
        self.currentPreviewGenerator = PreviewGenerator()
        self.totalPreviewGenerator = PreviewGenerator()
    
    def toggleAutoUpdate(self):
        if self.ui.preview_group.isChecked():
            if not self.previewTimer.isActive():
                self.updateRecordingInterval()
                self.previewTimer.start()
        else:
            if self.previewTimer.isActive():
                self.previewTimer.stop()
    
    def updateRecordingInterval(self):
        self.recorderThread.length = verify(self.ui.intervalSettings_length.text().toFloat(), 0.5, "recording interval", self)
    
    def startRecording(self):
        length = self.ui.intervalSettings_length.text().toFloat()
        if length[1]:
            length = length[0]
        else:
            print "invalid length"
            self.ui.statusbar.message("Invalid interval format")
            length = 0.5
        self.recorderThread = Recorder(length)
        self.recorderThread.start(QThread.TimeCriticalPriority)
        self.recorderThread.finished.connect(self.handleRecordFinished)
    
    def refreshPreview(self):
        if not self.currentPreviewGenerator.isRunning():
            self.dataAccessMutex.lock()
            self.currentPreviewGenerator.data = self.lastChunk
            self.dataAccessMutex.unlock()
            self.currentPreviewGenerator.widget = self.ui.plot_current
            self.currentPreviewGenerator.start()
    
    def handleProcessedData(self):
        self.dataAccessMutex.lock()
        self.lastChunk = self.dataProcessor.data
        self.dataAccessMutex.unlock()
    
    def handleQueuedData(self):
        print "processing data queue"
        self.dataAccessMutex.lock()
        self.dataProcessor.data = self.dataQueue
        self.dataProcessor.save = not self.ui.record_startstop.isEnabled()
        self.dataProcessor.integrationInterval = self.ui.intervalSettings_integrate.text().toInt()[0]
        filenameForChunk = self.ui.record_url.url().path() + "/" + self.ui.record_prefix.text() + "%04i" % self.chunkIndex
        self.dataProcessor.filename = filenameForChunk
        self.dataProcessor.finished.connect(self.handleProcessedData)
        self.dataProcessor.start()
        self.dataAccessMutex.unlock()
    
    def handleRecordFinished(self):
        data = self.recorderThread.data
        
        self.recorderThread.cleanup()
        self.recorderThread.start(QThread.TimeCriticalPriority)
        
        self.dataAccessMutex.lock()
        self.dataQueue = data
        self.dataAccessMutex.unlock()
        self.handleQueuedData()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = mainwin()
    w.show()
    sys.exit(app.exec_())
