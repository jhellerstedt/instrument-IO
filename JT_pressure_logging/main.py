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
from bokeh.layouts import column, row, layout

import read_pressures
from read_pressures import update_interval, rollover_interval


plot_source = ColumnDataSource(data=dict(x=[], LL_pressure=[], prep_pressure=[], microscope_pressure=[]))


TOOLS="resize,pan,wheel_zoom,box_zoom,reset,box_select,save"

## LL pressure plot

LL_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=350, plot_height=350) # , lod_factor=16, lod_threshold=10

LL_p.y_range.range_padding=0

LL_p.xaxis.axis_label = "time"
LL_p.xaxis.formatter=DatetimeTickFormatter()

LL_p.yaxis.axis_label = "LL pressure (mbar)"

LL_r = LL_p.line(x='x', y='LL_pressure', source=plot_source)

## prep pressure plot

prep_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=350, plot_height=350) # , lod_factor=16, lod_threshold=10

prep_p.y_range.range_padding=0

prep_p.xaxis.axis_label = "time"
prep_p.xaxis.formatter=DatetimeTickFormatter()

prep_p.yaxis.axis_label = "prep pressure (mbar)"

prep_r = prep_p.line(x='x', y='prep_pressure', source=plot_source)

## microscope pressure plot

micro_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=350, plot_height=350) # , lod_factor=16, lod_threshold=10

micro_p.y_range.range_padding=0

micro_p.xaxis.axis_label = "time"
micro_p.xaxis.formatter=DatetimeTickFormatter()

micro_p.yaxis.axis_label = "microscope pressure (mbar)"

micro_r = micro_p.line(x='x', y='microscope_pressure', source=plot_source)

## remove zero's for plotting:
    
for aa, ii, jj, kk in zip(read_pressures.source.data['x'], read_pressures.source.data['LL_pressure'], 
                            read_pressures.source.data['prep_pressure'], 
                            read_pressures.source.data['microscope_pressure']):
    if ii <= 0.:
        ii = 1
    if jj <= 0.:
        ii = 1
    if kk <= 0.:
        kk = 1
    plot_source.stream(dict(x=[aa], LL_pressure=[ii], prep_pressure=[jj], microscope_pressure=[kk]), rollover=rollover_interval)
    


def plot_update():
    try:
        temp_time = read_pressures.source.data['x'][-1]
        LL_temp = read_pressures.source.data['LL_pressure'][-1]
        if LL_temp == 0.:
            LL_temp = 1
        prep_temp = read_pressures.source.data['prep_pressure'][-1]
        if prep_temp == 0.:
            prep_temp = 1
        micro_temp = read_pressures.source.data['microscope_pressure'][-1]
        if micro_temp == 0.:
            micro_temp = 1
        
        plot_source.stream(dict(x=[temp_time],
            LL_pressure=[LL_temp],
            prep_pressure=[prep_temp],
            microscope_pressure=[micro_temp]), 
            rollover=rollover_interval)
            
        LL_display.value = str(read_pressures.source.data['LL_pressure'][-1])
        prep_display.value = str(read_pressures.source.data['prep_pressure'][-1])
        micro_display.value = str(read_pressures.source.data['microscope_pressure'][-1])
    except:
        print("something wrong in main")
        print(read_pressures.source)
        pass
        


    

LL_display = TextInput(title="LL pressure", value=" ")
prep_display = TextInput(title="prep pressure", value=" ")
micro_display = TextInput(title="microscope pressure", value=" ")

# layout = row(LL_p, LL_display, prep_p, prep_display, micro_p, micro_display)


l = layout([LL_display, prep_display, micro_display], 
            [LL_p, prep_p, micro_p],
            sizing_mode='scale_both')
curdoc().add_root(l)

curdoc().title = "JT pressure status"
curdoc().add_periodic_callback(plot_update, update_interval)




    
