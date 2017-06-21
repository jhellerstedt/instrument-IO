#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 20 Feb 2017


NOTE
this can only be called every 2 SECONDS or the gauge serial communication pukes

@author: jack
"""

import serial
import time

global ser

def TPG_open_serial(serial_address):
    global ser
    try:
        ser = serial.Serial(
            port=serial_address,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=3
        )
    except serial.SerialException as e:
        print(e)
        return
    return
    
def TPG_close_serial(serial_address):
    global ser
    try:
        ser.close()
    except serial.SerialException as e:
        print(e)
        return
    return


##call this once to tell gauge to return gauge 1 value
def TPG_read_gauge1():
    ser.write(b'PR1\r') ## command to read gauge 1
    ## should return  ACK (hex 06) CR LF
    return ser.readline()


def TPG_read_pressure():
    answer = '1'
    try:   
        ## ASCII for ENQ ENQUIRY, hexidecimal 05, pg. 65 pfeiffer manual
        ser.write(b'\x05')
        time.sleep(.3)
        answer = ser.readline().decode('utf-8')
        
    except serial.SerialException as e:
        print(e)
        return 0.

    if answer[0] == '0':
        return float(answer[3:13]) ## these are the digits of the pressure, convert to float
    else:
        return 0.