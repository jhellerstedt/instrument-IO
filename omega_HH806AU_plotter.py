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
import datetime

import omega_HH806AU as omega


from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.models.widgets import TextInput, Button
from bokeh.layouts import column, row

from tornado import gen


### set serial address
serial_address = '/dev/cu.usbserial-AL00R9JJ'

##open the connection
omega.HH806AU_open_connection(serial_address)


## set the log filename as a string
log_filename = "example.txt"


### if the update_interval callback is 2000 ms or less, too fast for reading the pressure gauge
update_interval = 700 ## ms
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

p.xaxis.formatter=DatetimeTickFormatter()

p.yaxis.axis_label = "temperature (C)"


r1 = p.line(x='x', y='y', source=source1, legend="T1 temp", color="red")
r2 = p.line(x='x', y='y', source=source2, legend="T2 temp", color="blue")


#### populate plot with old data if possible:

try:
    f = open(log_filename)
    for line in iter(f):
        ts, t1, t2 = str.split(line, '\t', 2)
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

global temp1_old, temp2_old
temp1_old, temp2_old = omega.HH806AU_read_temp()

global timer_zero
timer_zero = time.time()


@gen.coroutine
def update():
    global t0, rollover_interval, first_run, log_interval, temp1_old, temp2_old, timer_zero
    global temp1, temp2
    
    ### replace with the function call to read the instrument you want
    temp1, temp2 = omega.HH806AU_read_temp()
        
    instrument_display1.value = str(temp1)
    instrument_display2.value = str(temp2)
        
    ts = dt.now()
    
    ## the 1e3 and 3600 are some weird bokeh correction, maybe a ms/ns problem, and timezone?
    if np.abs(temp1 - temp1_old) < 50:
        source1.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[temp1]),rollover=rollover_interval)
        temp1_old = temp1
    if np.abs(temp2 - temp2_old) < 50:
        source2.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[temp2]),rollover=rollover_interval)
        temp2_old = temp2    
  
    t1 = time.time()
    # timer_display.value = "{:.2}".format((t1-timer_zero)/60)
    timer_display.value = str(datetime.timedelta(seconds=int(round(t1-timer_zero))))
    
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

timer_display = TextInput(title="timer", value=" ")
reset_button = Button(label="reset", button_type="default")

@gen.coroutine
def reset_timer():
    global timer_zero
    timer_zero = time.time()
    
reset_button.on_click(reset_timer)


data_values = column(instrument_display1, instrument_display2, timer_display, reset_button)

layout = row(p,data_values)


curdoc().add_root(layout)
curdoc().title = "omega temperature logging"
curdoc().add_periodic_callback(update, update_interval)
    
