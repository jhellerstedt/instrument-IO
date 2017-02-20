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

from datetime import datetime as dt

import omega_HH806AU as omega


from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.models.widgets import TextInput
from bokeh.layouts import column, row



### set serial address
serial_address = '/dev/cu.usbserial-AL00R9JJ'


## set the log filename as a string
log_filename = "example.txt"


### if the update_interval callback is 2000 ms or less, too fast for reading the pressure gauge
update_interval = 500 ## ms
total_axis_hours = 24 ## total hours to keep in bokeh plot
log_interval = 30 ## minutes interval to write data points to log file


log_interval = log_interval * 60
total_axis_hours = np.multiply(total_axis_hours,3.6e6)

global rollover_interval
rollover_interval = int(np.floor(np.divide(total_axis_hours, update_interval)))




source1 = ColumnDataSource(data=dict(x=[], y=[]))
source2 = ColumnDataSource(data=dict(x=[], y=[]))

TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,save"

p = figure(tools=TOOLS, x_axis_type="datetime") # , lod_factor=16, lod_threshold=10 , y_axis_type="log"

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

p.yaxis.axis_label = "temperature (C)"


r1 = p.line(x='x', y='y', source=source1, legend="T1 temp", color="red")
r2 = p.line(x='x', y='y', source=source2, legend="T2 temp", color="blue")


#### populate plot with old data if possible:

try:
    f = open(log_filename)
    for line in iter(f):
        ts, t1, t2 = str.split(line, '\t', 1)
        ts = dt.strptime(ts, "%Y-%m-%d %H:%M:%S")
        t1 = float(t1)
        t2 = float(t2)
        source1.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[t1]),rollover=rollover_interval)
        source2.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[t2]),rollover=rollover_interval)
    f.close()
except:
    pass

    
    
global t0, first_run
t0 = time.time()
first_run = True


def update():
    global t0, rollover_interval, first_run, log_interval
    
    
    ### replace with the function call to read the instrument you want
    read_value = 1
    temp1, temp2 = omega.HH806AUtemperature(serial_address)
        
    instrument_display1.value = str(temp1)
    instrument_display2.value = str(temp2)
        
    ts = dt.now()
    ## the 1e3 and 3600 are some weird bokeh correction, maybe a ms/ns problem, and timezone?
    source1.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[temp1]),rollover=rollover_interval)
    source2.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[temp2]),rollover=rollover_interval)
    
  
    t1 = time.time()
    if t1 - t0 > log_interval or first_run == True:  ## take a log point every thirty minutes    
        first_run = False
        ts = str(ts)
        ts = ts[:19]
        log = open(log_filename, 'a')
        log.write(ts + "\t" + str(temp1) + "\t" + str(temp2) + "\n")
        log.close()
        t0 = t1

    

instrument_display1 = TextInput(title="T1", value=" ")
instrument_display2 = TextInput(title="T2", value=" ")

data_values = column(instrument_display1, instrument_display2)

layout = row(p,data_values)


curdoc().add_root(layout)
curdoc().title = "generic real-time plotter with logging"
curdoc().add_periodic_callback(update, update_interval)
    
