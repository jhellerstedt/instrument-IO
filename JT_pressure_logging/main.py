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
from bokeh.models.widgets import TextInput, Button, DatePicker, Dropdown
from bokeh.layouts import column, row, layout

import read_pressures
from read_pressures import update_interval, LL_temp, prep_temp, micro_temp, log_filename
from read_pressures import rollover_interval as read_rollover_interval


total_axis_hours = 24
total_axis_hours = np.multiply(total_axis_hours,3.6e6) ## hours to ms
rollover_interval = int(np.floor(np.divide(total_axis_hours, update_interval)))


plot_source = ColumnDataSource(data=dict(x=[], LL_pressure=[], prep_pressure=[], microscope_pressure=[]))

historical_source = ColumnDataSource(data=dict(x=[], y=[]))




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

### historical range plot:

hist_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=350, plot_height=350) # , lod_factor=16, lod_threshold=10

hist_p.y_range.range_padding=0

hist_p.xaxis.axis_label = "time"
hist_p.xaxis.formatter=DatetimeTickFormatter()

hist_p.yaxis.axis_label = "pressure (mbar)"

hist_r = hist_p.line(x='x', y='y', source=historical_source)


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
    plot_source.stream(dict(x=[aa], LL_pressure=[ii], prep_pressure=[jj], microscope_pressure=[kk]), rollover=read_rollover_interval)
    


def plot_update():
    try:
        temp_time = (dt.timestamp(dt.now())+3600)*1e3
        # LL_temp = read_pressures.source.data['LL_pressure'][-1]
        # if LL_temp == 0.:
        #     LL_temp = 1
        # prep_temp = read_pressures.source.data['prep_pressure'][-1]
        # if prep_temp == 0.:
        #     prep_temp = 1
        # micro_temp = read_pressures.source.data['microscope_pressure'][-1]
        # if micro_temp == 0.:
        #     micro_temp = 1
        
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
        

def log_history_update(channel_selected, start_date, end_date):
    
    historical_source = ColumnDataSource(data=dict(x=[], LL_pressure=[], prep_pressure=[], 
                                            microscope_pressure=[]))    
    
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
            if ts > dt.strptime(start_date, "%Y-%m-%d") and ts < dt.strptime(end_date, "%Y-%m-%d"):
                if channel_selected == "LL_pressure":
                    historical_source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[LL_temp]))
                if channel_selected == "prep_pressure":
                    historical_source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[prep_temp]))
                if channel_selected == "microscope_pressure":
                    historical_source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[micro_temp]))
        f.close()
    except:
        pass


    

LL_display = TextInput(title="LL pressure", value=" ")
prep_display = TextInput(title="prep pressure", value=" ")
micro_display = TextInput(title="microscope pressure", value=" ")

### widgets for historical data display:

menu = [("LL pressure", "LL_pressure"), ("prep pressure", "prep_pressue"), ("microscope", "microscope_pressure")]
channel_selection = Dropdown(label="select channel", button_type="success", menu=menu)
# start_date_widget = DatePicker(title="start date", min_date=dt(2017,1,1), max_date=dt.now(), value=dt(dt.now().year,1,1))
# end_date_widget = DatePicker(title="end date", min_date=dt(2017,1,1), max_date=dt.now(), value=dt(dt.now().year,1,1))
start_date_widget = TextInput(title="start date (YYYY-MM-DD)", value=" ")
end_date_widget = TextInput(title="end date (YYYY-MM-DD)", value=" ")
update_hist_data = Button(label="update plot")

##callback to update history plot:
def update_plot():
    log_history_update(channel_selection.value, start_date_widget.value, end_date_widget.value)
    return
update_hist_data.on_click(update_plot)

# hist_layout = column(hist_p, column(channel_selection, start_date_widget, end_date_widget, update_hist_data))



l = layout([LL_display, prep_display, micro_display], 
            [LL_p, prep_p, micro_p],
            sizing_mode='scale_width')
            
# l2 = column(l, hist_layout)
curdoc().add_root(l)

curdoc().title = "JT pressure status"
curdoc().add_periodic_callback(plot_update, update_interval)




    
