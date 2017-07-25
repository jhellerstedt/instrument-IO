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

import read_temps
from read_temps import source1, source2, update_interval, total_axis_hours, log_interval, rollover_interval


total_axis_hours = 24 ## total hours to keep in bokeh plot

total_axis_hours = np.multiply(total_axis_hours,3.6e6)

global rollover_interval
rollover_interval = int(np.floor(np.divide(total_axis_hours, update_interval)))

global timer_zero
timer_zero = time.time()

TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,save"

p = figure(tools=TOOLS, x_axis_type="datetime") # , lod_factor=16, lod_threshold=10 , y_axis_type="log"

p.y_range.range_padding=0

p.xaxis.axis_label = "time"

p.xaxis.formatter=DatetimeTickFormatter()

p.yaxis.axis_label = "temperature (C)"

plot_source1 = ColumnDataSource(data=dict(x=[], y=[]))
plot_source2 = ColumnDataSource(data=dict(x=[], y=[])) 


r1 = p.line(x='x', y='y', source=plot_source1, legend="T1 temp", color="red")
r2 = p.line(x='x', y='y', source=plot_source2, legend="T2 temp", color="blue")

for ii, jj in zip(read_temps.source1.data['x'], read_temps.source1.data['y']):
    plot_source1.stream(dict(x=[ii], y=[jj]),rollover=rollover_interval)
for ii, jj in zip(read_temps.source2.data['x'], read_temps.source2.data['y']):    
    plot_source2.stream(dict(x=[ii], y=[jj]),rollover=rollover_interval)
   

@gen.coroutine
def plot_update():
    global t0, rollover_interval, first_run, log_interval, timer_zero
    
    instrument_display1.value = str(read_temps.temp1)
    instrument_display2.value = str(read_temps.temp2)
    
    ts = dt.now()

    ## the 1e3 and 3600 are some weird bokeh correction, maybe a ms/ns problem, and timezone?
    plot_source1.stream(dict(x=[read_temps.source1.data['x'][-1]], y=[read_temps.source1.data['y'][-1]]),rollover=rollover_interval)
    plot_source2.stream(dict(x=[read_temps.source2.data['x'][-1]], y=[read_temps.source2.data['y'][-1]]),rollover=rollover_interval) 

    t1 = time.time()
    timer_display.value = str(datetime.timedelta(seconds=int(round(t1-timer_zero))))

          

instrument_display1 = TextInput(title="T1", value=" ")
instrument_display2 = TextInput(title="T2", value=" ")

timer_display = TextInput(title="timer", value=" ")
reset_button = Button(label="reset", button_type="default")

@gen.coroutine
def reset_timer():
    global timer_zero
    timer_zero = time.time()
    
def initialize():
    if start_update.label == 'start communication':
        start_update.label = 'stop communication'
    elif start_update.label == 'stop communication':
        start_update.label = 'start communication'
    read_temps.initialize(instrument_address.value)
    
reset_button.on_click(reset_timer)

instrument_address = TextInput(title='address', value='/dev/ttyUSB3')

start_update = Button(label="start communication", button_type="default")
start_update.on_click(initialize)


data_values = column(instrument_address, start_update, instrument_display1, instrument_display2, timer_display, reset_button)

layout = row(p,data_values)


curdoc().add_root(layout)
curdoc().title = "omega temperature logging"
curdoc().add_periodic_callback(plot_update, update_interval)
    
