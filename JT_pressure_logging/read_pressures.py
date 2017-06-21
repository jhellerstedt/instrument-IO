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
#import pandas as pd

from datetime import datetime as dt

#import matplotlib.pyplot as plt


from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.models.widgets import TextInput
from bokeh.layouts import column, row

import pfeiffer_TPG261 as LL_gauge
import vacom_MVC3 as prep_gauge
import vacom_MVC3 as micro_gauge

### initialize gauges:
LL_gauge.TPG_open_serial('/dev/ttyUSB2')
confirmation = LL_gauge.TPG_read_gauge1()

prep_gauge.VACOM_open_serial('/dev/ttyUSB0')
micro_gauge.VACOM_open_serial('/dev/ttyUSB1')


## set the log filename as a string
log_filename = "JT_pressure_logging/JT_pressure_log.txt"


### if the update_interval callback is 2000 ms or less, too fast for reading the pressure gauge
update_interval = 5000 ## ms
total_axis_hours = 24 ## total hours to keep in bokeh plot
log_interval = 30 ## minutes interval to write data points to log file

log_interval = log_interval * 60
total_axis_hours = np.multiply(total_axis_hours,3.6e6)

global rollover_interval
rollover_interval = int(np.floor(np.divide(total_axis_hours, update_interval)))

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
        prep_temp = float(prep_temp)
        micro_temp = float(micro_temp)
        source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], LL_pressure=[LL_temp], prep_pressure=[prep_temp], microscope_pressure=[micro_temp]),rollover=rollover_interval)
    f.close()
except FileNotFoundError:
    pass    
    
global t0, first_run
t0 = time.time()
first_run = True


def update():
    global t0, rollover_interval, first_run, log_interval
    
    while True:
        time.sleep(update_interval/1e3) ##convert ms to s
        try:
            ### replace with the function call to read the instrument you want
            LL_temp = LL_gauge.TPG_read_pressure()
            prep_temp = prep_gauge.VACOM_read_pressure()
            micro_temp = micro_gauge.VACOM_read_pressure()
        
            ts = dt.now()
            ## the 1e3 and 3600 are some weird bokeh correction, maybe a ms/ns problem, and timezone?
            source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], LL_pressure=[LL_temp], prep_pressure=[prep_temp], microscope_pressure=[micro_temp]),rollover=rollover_interval)
  
            t1 = time.time()
            if t1 - t0 > log_interval or first_run == True:  ## take a log point every thirty minutes    
                first_run = False
                ts = str(ts)
                ts = ts[:19]
                log = open(log_filename, 'a')
                log.write(ts + "\t" + str(LL_temp) + "\t" + str(prep_temp) + "\t" + str(micro_temp) + "\n")
                log.close()
                t0 = t1
        except:
            print("something wrong with gauge read")
            continue
        

    
