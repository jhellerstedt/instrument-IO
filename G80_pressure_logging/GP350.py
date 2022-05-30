#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2020-9-4

GP350 ion gauge controller serial pressure read

author: Jack
"""

import serial
import time


def read_pressure(serial_address):
    
    if serial_address == 'test':
        return 3.14159
    
    
    try:
        ser = serial.Serial(
            port=serial_address,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2
        )

        read_command = "#RD\r" ##GP350
        read_command = bytes(read_command, 'utf-8')

        ser.write(read_command)
        time.sleep(.3)
        answer = ser.read_until('\r').decode('utf-8')
    
        pressure = float(answer.split('\r')[0].split(' ')[1])
        
        if pressure == 9.9E9:
            ## gauge probably off, set to nan
            pressure = float('nan')
        
    except:
        pressure = float('nan')
    
    return pressure