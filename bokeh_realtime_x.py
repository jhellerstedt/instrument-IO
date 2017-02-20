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


## set the log filename as a string
log_filename = "example.txt"


### if the update_interval callback is 2000 ms or less, too fast for reading the pressure gauge
update_interval = 5000 ## ms
total_axis_hours = 24 ## total hours to keep in bokeh plot
log_interval = 30 ## minutes interval to write data points to log file


log_interval = log_interval * 60
total_axis_hours = np.multiply(total_axis_hours,3.6e6)

global rollover_interval
rollover_interval = int(np.floor(np.divide(total_axis_hours, update_interval)))




source = ColumnDataSource(data=dict(x=[], y=[]))

TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,save"

p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime") # , lod_factor=16, lod_threshold=10

p.y_range.range_padding=0

p.xaxis.axis_label = "time"
p.xaxis.formatter=DatetimeTickFormatter()

##removed the following from DatetimeTickFormatter because of bokeh 0.12.4 update
# formats=dict(
#      microseconds=["%k %M %S"],
#      milliseconds=["%k %M %S"],
#      seconds=["%k %M %S"],
#      minsec=["%k %M %S"],
#      minutes=["%k %M %S"],
#      hourmin=["%k %M"],
#      hours=["%k %M"],
#      days=["%d %k %M"],
#      months=["%d %k %M"],
#      years=["%Y %d %k %M"]
#     )


p.yaxis.axis_label = "pressure (mbar)"


r = p.line(x='x', y='y', source=source)


#### populate plot with old data if possible:

try:
    f = open(log_filename)
    for line in iter(f):
        ts, pressure = str.split(line, '\t', 1)
        ts = dt.strptime(ts, "%Y-%m-%d %H:%M:%S")
        pressure = float(pressure)
        source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[pressure]),rollover=rollover_interval)
    f.close()
except FileNotFoundError:
    pass

    
    
global t0, first_run
t0 = time.time()
first_run = True


def update():
    global t0, rollover_interval, first_run, log_interval
    
    
    ### replace with the function call to read the instrument you want
    read_value = 1
        
    instrument_display.value = str(read_value)
        
    ts = dt.now()
    ## the 1e3 and 3600 are some weird bokeh correction, maybe a ms/ns problem, and timezone?
    source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[read_value]),rollover=rollover_interval)
  
    t1 = time.time()
    if t1 - t0 > log_interval or first_run == True:  ## take a log point every thirty minutes    
        first_run = False
        ts = str(ts)
        ts = ts[:19]
        log = open(log_filename, 'a')
        log.write(ts + "\t" + str(read_value) + "\n")
        log.close()
        t0 = t1

    

instrument_display = TextInput(title="instrument name", value=" ")

layout = row(p,instrument_display)


curdoc().add_root(layout)
curdoc().title = "generic real-time plotter with logging"
curdoc().add_periodic_callback(update, update_interval)
    
