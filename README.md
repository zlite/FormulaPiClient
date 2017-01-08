# FormulaPiClient
This is the RaspberryPi client side of a distributed version of the FormulaPi code running remotely on a PC. 
The core FormulaPi code is not open source, so I can't share it, but this is my own code to modify it. You can get the full FormulaPi code by signing up here: http://formulapi.com/

This code runs on a RaspberryPi on the rover, while the actual FormulaPi code runs on a remote PC for processing effeciency. 
They talk to each other over WiFi using a standard TCP socket method.

This is designed to work with a RasPiRobot V3 motor driver board (https://www.adafruit.com/product/1940) but can be easily modified for any other motor driver board.

The video is sent from the RPi to the PC using this method. http://petrkout.com/electronics/low-latency-0-4-s-video-streaming-from-raspberry-pi-mjpeg-streamer-opencv/
