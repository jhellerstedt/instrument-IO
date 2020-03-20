#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 29 Jan 2020

independent function for reading GP350 pressure over a serial connection

call function by pressure gauge serial address

function returns pressure on gauge as a float
otherwise it pukes and returns 0

NOTE
this can only be called every 2 SECONDS or the gauge serial communication pukes

@author: jack/ Travis Hartley
"""

import serial
import time

global ser

def GP350_open_serial(serial_address):
    global ser
    try:
        ser = serial.Serial(
            port=serial_address,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=2
        )
    except serial.SerialException as e:
        print(e)
        return
    return
    
def GP350_close_serial(serial_address):
    global ser
    try:
        ser.close()
    except serial.SerialException as e:
        print(e)
        return
    return


def GP350_read_pressure():
    pressure = '10'
    
    try:   
        read_command = "#RD\r" ## for GP350
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
        return 0.
    try:
        if pressure[0] == '0':
            return pressure[3:-1]
        else:
            return float(pressure[1:-1])
    except:
        return 0.
