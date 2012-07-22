import fcntl
import struct
from math import *
import sys
import subprocess
from time import sleep
import os

def log(string):
    sys.stderr.write(string + "\n")

def log(string):
    pass

def detectI2CTinyUSB():
    log("Scanning for i2c-tiny-usb...")
    try:
        dev = subprocess.check_output("i2cdetect -l |grep 'i2c-tiny-usb'", shell=True)
        dev = dev.split("\t")
        dev = "/dev/" + dev[0]
        log("i2c-tiny-usb found at %s." % dev)
        return dev
    except subprocess.CalledProcessError:
        raise IOError("Could not detect any i2c-tiny-usb devices! Make sure the device is plugged in.")

def stringToDecimal(raw_data):
    result = ord(raw_data[0])*256 + ord(raw_data[1])
    # the idiot way to handle the parity bit
    if result > 2**15:
        result -= 2**16
    return result

class i2cConnection():
    def __init__(self):
        self.deviceFile = None
        self.deviceUrl = None
    
    def __del__(self):
        if self.deviceFile is not None:
            log("Closing device file.")
            self.deviceFile.close()

    def openDevice(self):
        self.deviceUrl = detectI2CTinyUSB()
        if not os.path.exists(self.deviceUrl) or not os.access(self.deviceUrl, os.W_OK):
            raise IOError("Failed to get write-access to device file.")
        self.deviceFile = open(self.deviceUrl, "r+b", 0)
        self.activate()
    
    def activate(self):
        assert self.deviceFile
        log("sending ioctl to device")
        if fcntl.ioctl(self.deviceFile, 0x0703, self.clientAddress) < 0:
            raise IOError("ioctl failed");

    def isInitialized(self):
        return hasattr(self, "operationMode")
    
    def reinit(self):
        log("re-initializing controller.")
        self.openDevice()
        self.deviceFile.write(chr(self.operationMode))
    
    def readBlock(self):
        while True:
            raw_data = self.deviceFile.read(3)
            if ord(raw_data[2]) & 128:
                # no new data ready to be read
                continue
            decimal = stringToDecimal(raw_data)
            return decimal
    
    def beginReadData(self):
        try:
            subsequentErrors = 0
            while True:
                try:
                    raw_data = self.deviceFile.read(3)
                    if ord(raw_data[2]) & 128:
                        # no new data ready to be read
                        continue
                    #print [bin(ord(item)) for item in raw_data]
                    subsequentErrors = 0
                except IOError:
                    log("I/O error occured while reading data, trying to recover")
                    subsequentErrors += 1
                    if ( subsequentErrors > 10 ):
                        raise IOError("device communication failed")
                    sleep(0.5)
                    self.reinit()
                    continue
                decimal = stringToDecimal(raw_data[0:2])
                print decimal
        except KeyboardInterrupt:
            log("Exiting because of user interrupt.")

class ds1629Client(i2cConnection):
    clientAddress = 0x4f
    
    def __init__(self):
        i2cConnection.__init__(self)
        high = (125.0, self.toInt(chr(0x7D)+chr(0x00)))
        low = (-55.0, self.toInt(chr(0xC9)+chr(0x00)))
        self.inputRange = high[1] - low[1]
        self.outputRange = high[0] - low[0]
        self.conversionFactor = self.outputRange / self.inputRange
    
    def toInt(self, data):
        intData = [ord(item) for item in data]
        if intData[0] & 0x80:
            return (intData[0] - 0xFF)*256 + (intData[1] - 0xFF)
        return stringToDecimal(data)
    
    def intToCelsius(self, item):
        return round(item * self.conversionFactor, 2)
    
    def beginReadData(self):
        while True:
            print self.readBlock()
            sleep(1)
    
    def readBlock(self):
        self.deviceFile.write(chr(0xEE))
        self.deviceFile.write(chr(0xAA))
        data = self.deviceFile.read(2)
        return self.intToCelsius(self.toInt(data))
        

class mcp3426Client(i2cConnection):
    clientAddress = 0x68
    
    def readBlock(self):
        while True:
            raw_data = self.deviceFile.read(3)
            if ord(raw_data[2]) & 128:
                # no new data ready to be read
                continue
            decimal = stringToDecimal(raw_data)
            return decimal
    
    def setOperationMode(self, rate = "16bit", gain = "1x"):
        rates = {"16bit": 0b10, "14bit": 0b01, "12bit": 0b00}
        gains = {"1x": 0b00, "2x": 0b01, "4x": 0b10, "8x": 0b11}
        ready = 0b1 << 7
        channel = 0b00 << 5
        mode = 0b1 << 4 # continuous
        rate = rates[rate] << 2 # sample rate
        gain = gains[gain] << 0 # gain multiplier
        cmd = ready + channel + mode + rate + gain
        self.operationMode = cmd
        log("Sending device operation mode command: %s." % bin(cmd))
        self.deviceFile.write(chr(cmd))

def scanForClients():
    print "Scanning for connected i2c clients."
    for device in range(0, 0x80):
        c = i2cConnection()
        c.clientAddress = device
        try:
            c.openDevice()
            c.readBlock()
            print "Success at address", hex(device)
        except IOError:
            continue

def ds1629Main():
    connection = ds1629Client()
    connection.openDevice()
    connection.beginReadData()

def mcp3426Main():
    connection = mcp3426Client()
    connection.openDevice()
    connection.setOperationMode("16bit", "1x")
    connection.beginReadData()

if __name__ == '__main__':
    if 'temperature' in sys.argv:
        ds1629Main()
    elif 'ad' in sys.argv:
        mcp3426Main()
    elif 'list' in sys.argv or len(sys.argv) == 1:
        scanForClients()
