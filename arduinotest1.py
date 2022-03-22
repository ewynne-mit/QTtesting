import sys
import os
import serial
import time

ser = serial.Serial('/dev/cu.usbmodem142301', 9600, timeout=1)

for i in range(10):
    time.sleep(0.5)
    ser.write(b'H')
    time.sleep(0.5)
    ser.write(b'L')