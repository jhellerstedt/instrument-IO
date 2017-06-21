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

update_interval = 5000 ## ms


plot_source = ColumnDataSource(data=dict(x=[], LL_pressure=[], prep_pressure=[], microscope_pressure=[]))


TOOLS="resize,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,save"

## LL pressure plot

LL_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime") # , lod_factor=16, lod_threshold=10

LL_p.y_range.range_padding=0

LL_p.xaxis.axis_label = "time"
LL_p.xaxis.formatter=DatetimeTickFormatter()

LL_p.yaxis.axis_label = "LL pressure (mbar)"

LL_r = LL_p.line(x='x', y='LL_pressure', source=plot_source)

## prep pressure plot

prep_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime") # , lod_factor=16, lod_threshold=10

prep_p.y_range.range_padding=0

prep_p.xaxis.axis_label = "time"
prep_p.xaxis.formatter=DatetimeTickFormatter()

prep_p.yaxis.axis_label = "prep pressure (mbar)"

prep_r = prep_p.line(x='x', y='prep_pressure', source=plot_source)

## microscope pressure plot

micro_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime") # , lod_factor=16, lod_threshold=10

micro_p.y_range.range_padding=0

micro_p.xaxis.axis_label = "time"
micro_p.xaxis.formatter=DatetimeTickFormatter()

micro_p.yaxis.axis_label = "microscope pressure (mbar)"

micro_r = micro_p.line(x='x', y='microsope_pressure', source=plot_source)


def plot_update():
    plot_source = read_pressures.source 
    LL_display.value = str(plot_source.data['LL_pressure'][-1])
    prep_display.value = str(plot_source.data['prep_pressure'][-1])
    micro_display.value = str(plot_source.data['microscope_pressure'][-1])
        


    

LL_display = TextInput(title="LL pressure", value=" ")
prep_display = TextInput(title="prep pressure", value=" ")
micro_display = TextInput(title="microscope pressure", value=" ")

layout = row(LL_p,LL_display, prep_p,prep_display, micro_p,micro_display)


curdoc().add_root(layout)
curdoc().title = "JT pressure status"
curdoc().add_periodic_callback(plot_update, update_interval)
    
