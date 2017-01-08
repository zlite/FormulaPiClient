# This is just a snippet of code that shows how the server side of the distributed
# FormulaPi code works. You'd plug this into the SimulationFull.py file to replace
# the code that talks to the simulator by simulating the motors

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

while True:
    YetiMotors(0.0, 0.0)
