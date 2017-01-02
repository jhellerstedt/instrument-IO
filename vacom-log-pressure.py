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
from bokeh.layouts import column

#configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='COM4',
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

### if the update_interval callback is 2000 ms or less, too fast for reading the pressure gauge
update_interval = 5000 ## ms
total_axis_hours = 24 ## total hours to keep in bokeh

total_axis_hours = np.multiply(total_axis_hours,3.6e6)

global rollover_interval
rollover_interval = int(np.floor(np.divide(total_axis_hours, update_interval)))



read_command = "RPV1,\r,OK" ## for VACOM MVC-3
read_command = bytes(read_command, 'utf-8')

time_array = []
pressure_array = []

source = ColumnDataSource(data=dict(x=[], y=[]))

TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,save"

p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime") # , lod_factor=16, lod_threshold=10

p.y_range.range_padding=0

p.xaxis.axis_label = "time"
p.xaxis.formatter=DatetimeTickFormatter(formats=dict(
     microseconds=["%k %M %S"],
     milliseconds=["%k %M %S"],
     seconds=["%k %M %S"],
     minsec=["%k %M %S"],
     minutes=["%k %M %S"],                                        
     hourmin=["%k %M"],
     hours=["%k %M"],
     days=["%d %k %M"],
     months=["%d %k %M"],
     years=["%Y %d %k %M"]          
    ))

p.yaxis.axis_label = "pressure (mbar)"


r = p.line(x='x', y='y', source=source)


#### populate plot with old data if possible:


old_data = os.popen('tail -n 10 pressure_log.txt').read()
while len(old_data) > 2:
    temp, old_data = str.split(old_data, '\n', 1)
    ts, pressure = str.split(temp, '\t', 1)
    ts = dt.strptime(ts, "%Y-%m-%d %H:%M:%S")
    pressure = float(pressure)
    source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[pressure]),rollover=rollover_interval)

global t0, first_run
t0 = time.time()
first_run = True


def update():
    global t0, rollover_interval, first_run

    ser.write(read_command)
    time.sleep(.3)
    pressure = ''
    while ser.inWaiting() > 0:
        pressure += ser.read(1).decode('utf-8')
        

    if pressure[0] == '0':
        pressure = float(pressure[3:-1])
        
        prep_pressure.value = str(pressure)
            
        ts = dt.now()
        ## the 1e3 and 3600 are some weird bokeh correction, maybe a ms/ns problem, and timezone?
        source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[pressure]),rollover=rollover_interval)
      
        t1 = time.time()
        if t1 - t0 > 1800 or first_run == True:  ## take a log point every thirty minutes    
            first_run = False
            ts = str(ts)
            ts = ts[:19]
            log = open("pressure_log.txt", 'a')
            log.write(ts + "\t" + str(pressure) + "\n")
            log.close()
            t0 = t1

    

prep_pressure = TextInput(title="prep pressure:", value=" ")

layout = column(p,prep_pressure)


curdoc().add_root(layout)
curdoc().title = "Logging VACOM pressure"
curdoc().add_periodic_callback(update, update_interval)
    
