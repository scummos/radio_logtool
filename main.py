import ossaudiodev
import wave
import sys
from struct import unpack, pack
from array import array
from time import time, sleep
from math import floor

class Recorder():
    def __init__(self):
        self.chunkSize = 1024
        self.format = ossaudiodev.AFMT_S16_LE
        self.channels = 1
        self.rate = 44100
    
    def record(self, length):
        """Record a chunk of "length" seconds, and return it as int array"""
        print "Recording block of length", length
        self.stream = ossaudiodev.open('r')
        self.stream.setfmt(self.format)
        self.stream.speed(self.rate)
        data = self.stream.read(int(length * self.rate * 2 + 2)) # 2 = sizeof(short)
        self.stream.close()
        return self.unpack(data)
    
    def unpack(self, data):
        return unpack('<' + ('h'*(len(data)/2)), data)
    
    def partition(self, data, length, integrationInterval = 1):
        blockSize = int(self.rate * length / integrationInterval)
        print "Partitioning data into blocks of", blockSize, "frames"
        size = len(data)
        atFrame = 0
        blocks = []
        while atFrame + blockSize <= size:
            blocks.append(data[atFrame:atFrame+blockSize])
            atFrame += blockSize
        return blocks
    
    def integrate(self, data, samples):
        newData = array('I', [])
        for rangeBegin in range(0, len(data), samples):
            newData.append(sum([x**2 for x in data[rangeBegin:rangeBegin+samples]]))
        return newData
    
    def addRegisteredBlocks(self, blocks):
        result = []
        for frameIndex in range(len(blocks[0])):
            result.append(sum([block[frameIndex] for block in blocks]))
        return result
    
    def writeArrayToDatafile(self, data, filename):
        print "Writing datafile %s" % filename
        with open(filename, 'w') as fileptr:
            for item in data:
                fileptr.write(str(item) + "\n")
    
if __name__ == '__main__':
    recorder = Recorder()
    data = recorder.record(50)
    integrated = recorder.integrate(data, 20)
    partitioned = recorder.partition(integrated, 1.0, 20)
    i = 0
    for part in partitioned:
        i += 1
        recorder.writeArrayToDatafile(part, "data/%04i.dat" % i)
    total = recorder.addRegisteredBlocks(partitioned)
    recorder.writeArrayToDatafile(total, "sum.dat")
    recorder.writeArrayToDatafile(data, "raw.dat")
