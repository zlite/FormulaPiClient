# This program receives commands from the FormulaPi code running on a remote PC
# and uses them to control the motors and LEDs of the rover
# Copyright 2017 by Chris Anderson, 3DR

import socket
import struct
from rrb3 import *
rr = RRB3(9, 6)

host = '192.168.86.35'      # Change this to the IP address of the PC you're communicating with
port = 12348                   # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
while True:
    buf = ''
    leftDir = 0
    rightDir = 0
    while len(buf) < 12:
        buf += s.recv(12)
    num = struct.unpack('!iff', buf)  # receive an integer for LED and two floats for motors
    print('LED ', num[0])
    print('Left motor: ',num[1])
    print('Right motor: ',num[2])
    if num[1] < 0:  # change direction if number is negative
            leftDir = 1
    if num[2] < 0:
            rightDir = 1
    rr.set_led1(num[0])
    rr.set_motors(abs(num[1]), leftDir, abs(num[2]), rightDir)
s.close()

