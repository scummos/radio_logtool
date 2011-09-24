import pyaudio
import wave
import sys
from struct import unpack, pack
from array import array

class Recorder():
    def __init__(self):
        self.chunkSize = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.p = pyaudio.PyAudio()
        self.stream = p.open(format = self.format, channels = self.channels, rate = self.rate,
                             input = True, frames_per_buffer = self.chunkSize)
    
    def numFrames(self, length):
        return length * self.rate / self.chunkSize
    
    def recordBlock(self, length):
        """Record a chunk of "length" seconds, and return it as int array"""
        collectedData = []
        for index in xrange(0, self.numFrames(length)):
            try:
                data = self.stream.read(self.chunkSize)
            except IOError:
                pass
            collectedData.append(data)
        
        unpackedData = array('h', [])
        for item in collectedData:
            unpackedItem = unpack('<' + ('h'*(len(data)/2)), item)
            unpackedData.extend(unpackedItem)
        return unpackedData
    
    def recordBlocked(self, totalLength, chunkLength):
        numChunks = totalLength / float(chunkLength)
        blocks = []
        for i in range(numChunks):
            currentBlock = recordBlock(chunkLength)
            blocks.append(currentChunk)
        return blocks
    
    def addRegisteredBlocks(self, blocks):
        result = []
        for frameIndex in len(blocks[0]):
            result.append(sum([block[frameIndex] for block in blocks]))
        return result
    
    def writeArrayToDatafile(self, data, filename):
        with open(filename, 'w') as fileptr:
            for item in data:
                fileptr.write(item + "\n")
    
if __name__ == '__main__':
    recorder = Recorder()
    data = recorder.recordBlocked(10, 1)
    total = recorder.addRegisteredBlocks(data)
    recorder.writeArrayToDatafile(total, "test.dat")