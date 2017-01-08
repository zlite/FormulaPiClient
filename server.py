# This is just a snippet of code that shows how the server side of the distributed
# FormulaPi code works. You'd plug this into the SimulationFull.py file to replace
# the code that talks to the simulator by simulating the motors

import time
import os
import sys
import threading
import cv2
import numpy
import random
import inspect
import Globals
import urllib2
import urllib
import socket
import struct
print 'Libraries loaded'

roverIP = ''            # Symbolic name meaning all available interfaces
roverPort = 12349       # Port number used by the rover code
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((roverIP, roverPort))
s.listen(1)
print ('Waiting to connect...')
conn, addr = s.accept()
print('Connected to', addr)

frameLimiter = True
stream=urllib.urlopen('http://192.168.137.126:8080/?action=stream') #Change to the IP address of your Raspberry Pi.
bytes=''

def YetiMotors(driveLeft, driveRight):
        global simLeft
        global simRight
        simLeft = driveLeft * Settings.simulationDrivePower
        simRight = driveRight * Settings.simulationDrivePower
        print '>>> MOTORS: %.3f | %.3f (x%.2f)' % (driveLeft, driveRight, Settings.simulationDrivePower)
        SendToSimulation()

def SendToSimulation():
        global simLed
        global simLeft
        global simRight
        val = struct.pack('!iff', simLed,simLeft,simRight)
        try:
                conn.sendall(val)
        except IOError:
                print 'Failed to send motor values to simulation!'
        except socket.error:
                print 'Failed to send motor values to simulation!'

def run(self):
        global bytes
        while Globals.running:
                # Grab the oldest unused processor thread
                with Globals.frameLock:
                        if Globals.processorPool:
                                processor = Globals.processorPool.pop()
                        else:
                                processor = None
                if processor:
                        # Grab the next frame from the simulation and send it to the processor
                        try:
                                flag = True
                                while flag == True:      
                                        bytes+=stream.read(1024) # this loads frames from the IP stream
                                        a = bytes.find('\xff\xd8')
                                        b = bytes.find('\xff\xd9')
                                        if a!=-1 and b!=-1:
                                                jpg = bytes[a:b+2]
                                                bytes = bytes[b+2:]
                                                frame = cv2.imdecode(numpy.fromstring(jpg, dtype=numpy.uint8),cv2.CV_LOAD_IMAGE_COLOR)
                                                flag = False
                                okay = True
                        except IOError:
                                okay = False
                        except urllib2.URLError:
                                okay = False
                        if frame == None:
                                # Something went wrong and the decode failed...
                                print '!!! BAD IMAGE !!!'
                                with Globals.frameLock:
                                        Globals.processorPool.insert(0, processor)
                                continue
                        if okay:
                                # Resize / crop the image if the resolution does not match
                                if (frame.shape[1] != Settings.imageWidth) or (frame.shape[0] != Settings.imageHeight):
                                        ratioIn = frame.shape[1] / float(frame.shape[0])
                                        ratioOut = Settings.imageWidth / float(Settings.imageHeight)
                                        if abs(ratioIn - ratioOut) < 0.01:
                                                # Straight resize
                                                pass
                                        elif ratioIn > ratioOut:
                                                # Crop width
                                                width = frame.shape[1]
                                                cropWidth = ratioOut / ratioIn
                                                cropOffset = (1.0 - cropWidth) / 2.0
                                                cropWidth = int(cropWidth * width)
                                                cropOffset = int(cropOffset * width)
                                                frame = frame[:, cropOffset : cropOffset + cropWidth, :]
                                        else:
                                                # Crop height
                                                height = frame.shape[0]
                                                cropHeight = ratioIn / ratioOut
                                                cropOffset = (1.0 - cropHeight) / 2.0
                                                cropHeight = int(cropHeight * height)
                                                cropOffset = int(cropOffset * height)
                                                frame = frame[cropOffset : cropOffset + cropHeight, :, :]
                                        frame = cv2.resize(frame, (Settings.imageWidth, Settings.imageHeight), interpolation = cv2.INTER_CUBIC)
                                # Generate a delay buffer to simulate camera lag
                                if self.lagFrames != Settings.simulationLagFrames:
                                        self.lagFrames = Settings.simulationLagFrames
                                        self.frameQueue = []
                                self.frameQueue.insert(0, frame)
                                if len(self.frameQueue) > self.lagFrames:
                                        frame = self.frameQueue.pop()
                                else:
                                        frame = numpy.zeros_like(frame)
                                processor.nextFrame = frame
                                processor.event.set()
                                # Work out the time delay required for the frame limiter
                                self.timeNow = time.time()
                                lagMs = (self.timeNow - self.timeLast) * 1000
                                self.timeLast = self.timeNow
                                self.holdMs = int(Globals.frameWaitMs - lagMs) + self.holdMs
                                if self.holdMs > 0:
                                        time.sleep(self.holdMs * 0.001)
                        else:
                                ImageProcessor.LogData(ImageProcessor.LOG_CRITICAL, 'Simulation stream lost...')
                                Globals.running = False
                                break
                else:
                        # When the pool is starved we wait a while to allow a processor to finish
                        time.sleep(0.01)
        ImageProcessor.LogData(ImageProcessor.LOG_CRITICAL, 'Streaming terminated.')

while True:
        run()
        YetiMotors(0.0, 0.0)
