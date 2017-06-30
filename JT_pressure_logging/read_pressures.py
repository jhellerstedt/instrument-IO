#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 17:29:28 2016

@author: jack
"""

import os
import time
import serial
import numpy as np
import math

from datetime import datetime as dt

#import matplotlib.pyplot as plt


from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.models.widgets import TextInput
from bokeh.layouts import column, row

import pfeiffer_TPG261 as LL_gauge
import vacom_MVC3

### initialize gauges:
def read_LL():
    LL_gauge.TPG_open_serial('/dev/ttyUSB2')
    LL_gauge.TPG_read_gauge1()
    pressure = LL_gauge.TPG_read_pressure()
    LL_gauge.TPG_close_serial('/dev/ttyUSB2')
    return pressure

def read_prep():
    vacom_MVC3.VACOM_open_serial('/dev/ttyUSB1')
    pressure = vacom_MVC3.VACOM_read_pressure()
    vacom_MVC3.VACOM_close_serial('/dev/ttyUSB1')
    return pressure

def read_micro():
    vacom_MVC3.VACOM_open_serial('/dev/ttyUSB0')
    pressure = vacom_MVC3.VACOM_read_pressure()
    vacom_MVC3.VACOM_close_serial('/dev/ttyUSB0')
    return pressure
    



## set the log filename as a string
log_filename = "/home/jack/instrument-IO/JT_pressure_logging/JT_pressure_log.txt"
# log_filename = os.getcwd() + "/" + log_filename
print(log_filename)


### if the update_interval callback is 2000 ms or less, too fast for reading the pressure gauge
update_interval = 5000 ## ms
data_interval = 3 ## minutes; spacing between data points in total_axis "buffer"
total_axis_hours = 24 ## total hours to keep in bokeh plot
log_interval = 10 ## minutes interval to write data points to log file

log_interval = log_interval * 60
total_axis_hours = np.multiply(total_axis_hours,3.6e6) ## hours to ms
data_interval = data_interval * 60 * 1e3 ## minutes to ms

global rollover_interval
rollover_interval = int(np.floor(np.divide(total_axis_hours, data_interval)))

source = ColumnDataSource(data=dict(x=[], LL_pressure=[], prep_pressure=[], microscope_pressure=[]))

#### populate plot with old data if possible:
try:
    f = open(log_filename)
    for line in iter(f):
        ts, pressure = str.split(line, '\t', 1)
        LL_temp, pressure = str.split(pressure, '\t', 1)
        prep_temp, micro_temp = str.split(pressure, '\t', 1)
        ts = dt.strptime(ts, "%Y-%m-%d %H:%M:%S")
        LL_temp = float(LL_temp)
        if math.isnan(LL_temp):
            LL_temp = 10.
        prep_temp = float(prep_temp)
        if math.isnan(prep_temp):
            prep_temp = 10.
        micro_temp = float(micro_temp)
        if math.isnan(micro_temp):
            micro_temp = 10.
        source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], LL_pressure=[LL_temp], prep_pressure=[prep_temp], microscope_pressure=[micro_temp]),rollover=rollover_interval)
    f.close()
except:
    print("log file read issues")
    pass    
    
global t0, t0_two, first_run
t0 = time.time()
t0_two = time.time()

first_run = True

global current_LL, current_prep, current_micro
current_LL = 0
current_prep = 0
current_micro = 0


def update():
    global t0, t0_two, rollover_interval, first_run, log_interval, current_LL, current_prep, current_micro
    
    while True:
        # print("sup reading gauges")
        time.sleep(update_interval/1e3) ##convert ms to s
        try:
            ### replace with the function call to read the instrument you want
            current_LL = read_LL()
            current_prep = read_prep()
            current_micro = read_micro()
        
            ts = dt.now()
            t1 = time.time()
            
            if t1 - t0_two > data_interval * 1e-3 or first_run == True:
                ## the 1e3 and 3600 are some weird bokeh correction, maybe a ms/ns problem, and timezone?
                source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], LL_pressure=[current_LL], prep_pressure=[current_prep], 
                                        microscope_pressure=[current_micro]),rollover=rollover_interval)
                t0_two = t1
  
            
            if t1 - t0 > log_interval or first_run == True:  ## take a log point every thirty minutes    
                first_run = False
                ts = str(ts)
                ts = ts[:19]
                log = open(log_filename, 'a')
                log.write(ts + "\t" + str(current_LL) + "\t" + str(current_prep) + "\t" + str(current_micro) + "\n")
                log.close()
                t0 = t1
        except:
            print("something wrong with gauge read")
            continue
            
