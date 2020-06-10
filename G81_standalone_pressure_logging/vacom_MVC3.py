#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 20 Feb 2017

independent function for reading VACOM MVC-3 pressure over a serial connection

call function by pressure gauge serial address

function returns pressure on gauge as a float
otherwise it pukes and returns 0

NOTE
this can only be called every 2 SECONDS or the gauge serial communication pukes

@author: jack
"""

import serial
import time

def read_pressure(serial_address):
    try:
        ser = serial.Serial(
                port=serial_address,
                baudrate=19200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=2
        )
        read_command = "RPV1,\r,OK" ## for VACOM MVC-3
        read_command = bytes(read_command, 'utf-8')
        
        ser.write(read_command)
        time.sleep(.3)
        answer = ser.read_until('\r').decode('utf-8')
        
        pressure = answer.split('\t')[1]
        pressure = float(pressure.split('\r')[0])
    except:
        pressure = float('nan')
    
    return pressure