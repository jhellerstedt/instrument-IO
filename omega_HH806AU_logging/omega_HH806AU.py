#!/usr/bin/env python
# This program shows how to read Omega HH806AU thermocouple meter T1 and T2 with Python3
#####################################################################################

# Modified from:
# https://github.com/artisan-roaster-scope/artisan/blob/master/src/CommHH806AUpython2.6.py

# #the HH806AU responds to "#0A0000NA2\r\n" with a bytes sequence that looks like:
# b'>\x0f\x00\x00 \x18 \x00\x00 \x0b\x01 \x18 \x00\x00 \x0b\x01\x95\x00'
# (spaces mine)
#
# see https://en.wikipedia.org/wiki/C0_and_C1_control_codes:
# from left to right:
# \x0f = shift in (to regular character set)
# \x00 \x00 = HH806AU id number (?)
#
# The next digit determines the sign of the temperature:
#
# \x18 = cancel, ignore data, e.g., no thermocouple attached to that channel
# \x10 = data comes next, e.g., the value is positive
# \x1f = unit separator, e.g., the value is negative
#
# the next two digits are hexadecimal for the temperature, ignore the first of the 4 hex characters
# (see hex2temp function)
#
# \x0b = line tab
# \x01 = first character of message header
#
# the next three digits are the same as above, for the T2 temperature
#
# \x0b\x01 new stuff
#
# \x95 = something about the battery state?
# \x00 = null

## 9.2.17 -JH



import serial
import time
import binascii

import asyncio

# serial_address = '/dev/cu.usbserial-AL00R9JJ'


global ser

def HH806AU_open_connection(serial_address):
    global ser
    try:
        ser = serial.Serial(serial_address, baudrate=19200, bytesize=8, parity='E', stopbits=1, timeout=1)
    except serial.SerialException as e:
        return e
    return
    
def HH806AU_close_connection():
    global ser
    try:
        ser.close()
    except:
        pass
    return

        
def hex2temp(h, sign):
    if h == '':
        return 0
    else:
        # t = int(h[1:],16)/10.0
        t = int(h,16)/10.0
        if sign == b'00':
            return 0
        if sign == b'1f':
            ### negative numbers are relative to b'ffff' = 65535
            t = (65535 - int(h,16))/10.0
            t = -t
            return t
        else:
            return t
            
def HH806AU_read_temp():
    global ser
    try:
        ###read command structure: # LL ID CH N checksum 0D0A
        ### LL = command length code (# + LL + ID + CH + N + check sum)byte
        ### ID = identification code, e.g. 00
        ### CH = channel identification, e.g. 00
        ### N = data access code, e.g., N
        ### check sum = hex of np.mod(sum(b"# LL ID CH N"), 256)
        ### e.g. A2 = hex of np.mod(sum(b"#0A0000N"), 256)
        
        command = b"#0A0000NA2\r\n"
        
        # command = b"#0A0001NA3\r\n"
        
        ser.reset_input_buffer()
        ser.write(command)       
        r = ser.read(15) ## this is fastest; longest time step
        
        ### !!!!! readline() times out according to the timeout set in ser  !!! don't use
        # r = ser.readline() ## use to read all information from omega
        
        

    except serial.SerialException as e:
        print(e)
        return 0,0
        
    except NameError:
        # return 0,0
        r = b'>\x0f\x00\x00\x10\x00\xf6\x0b\x01\x10\x00\xfb\x0b\x01v\x00'
        
    try:
        t1 = hex2temp(binascii.hexlify(r[5:7]), binascii.hexlify(r[4:5]))
        t2 = hex2temp(binascii.hexlify(r[10:12]), binascii.hexlify(r[9:10]))
    except:
        return 0,0
    
    return t1,t2
