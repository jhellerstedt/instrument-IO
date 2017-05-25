#!/usr/bin/env python

import serial
import time
import binascii

serial_address = '/dev/cu.usbserial-FT95OGZT'

global ser

def open_communication(serial_address=serial_address):
    global ser
    ser = serial.Serial(serial_address, timeout=1)
    
def close_communication():
    global ser
    ser.close()

def read_temp():
    global ser
    ser.write(b'?\n')
    r = ser.readline()
    print(r)