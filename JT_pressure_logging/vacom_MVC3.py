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

global ser

def VACOM_open_serial(serial_address):
    global ser
    try:
        ser = serial.Serial(
            port=serial_address,
            baudrate=19200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2
        )
    except serial.SerialException as e:
        print(e)
        return
    return
    
def VACOM_close_serial(serial_address):
    global ser
    try:
        ser.close()
    except serial.SerialException as e:
        print(e)
        return
    return


def VACOM_read_pressure():
    pressure = '10'
    
    try:   
        read_command = "RPV1,\r,OK" ## for VACOM MVC-3
        read_command = bytes(read_command, 'utf-8')
           
        tries = 0
    
        while pressure[0] != '0' and tries<1:
            ser.write(read_command)
            time.sleep(.3)
            pressure = ''
            ser_tries = 0
            while ser.inWaiting() > 0 and ser_tries < 15:
                pressure += ser.read(1).decode('utf-8')
                ser_tries = ser_tries+1      
            tries = tries + 1
            time.sleep(.2)
        
    except serial.SerialException as e:
        print(e)
        return float('nan')
    try:
        if pressure[0] == '0':
            return float(pressure[3:-1])
        else:
            return float('nan')
    except:
        return float('nan')