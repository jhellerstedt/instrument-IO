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

from tornado import gen

import datetime
from datetime import datetime as dt
from datetime import timedelta

#import matplotlib.pyplot as plt

from bokeh.client import push_session
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, WheelZoomTool
from bokeh.models.widgets import TextInput, Button, DatePicker, Dropdown, PreText
from bokeh.layouts import column, row, layout, widgetbox

import read_pressures

from read_pressures import update_interval, current_LL, current_prep, current_micro, log_filename
from read_pressures import rollover_interval as read_rollover_interval


total_axis_hours = 24
total_axis_hours = np.multiply(total_axis_hours,3.6e6) ## hours to ms
rollover_interval = int(np.floor(np.divide(total_axis_hours, update_interval)))


plot_source = ColumnDataSource(data=dict(x=[], LL_pressure=[], prep_pressure=[], microscope_pressure=[]))

# historical_source = ColumnDataSource(data=dict(x=[(dt.timestamp(dt.now())+3600)*1e3], y=[1]))
historical_source = ColumnDataSource(data=dict(x=[], y=[]))




TOOLS="resize,pan,wheel_zoom,box_zoom,reset,box_select,save"
wheel_zoom = WheelZoomTool()

## LL pressure plot

plot_width=400
plot_height=400

LL_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=plot_width, plot_height=plot_height)
LL_p.toolbar.active_scroll = wheel_zoom

LL_p.y_range.range_padding=0

LL_p.xaxis.axis_label = "time"
LL_p.xaxis.formatter=DatetimeTickFormatter()

LL_p.yaxis.axis_label = "LL pressure (mbar)"

LL_r = LL_p.line(x='x', y='LL_pressure', source=plot_source)

## prep pressure plot

prep_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=plot_width, plot_height=plot_height)
# prep_p.toolbar.active_scroll = wheel_zoom

prep_p.y_range.range_padding=0

prep_p.xaxis.axis_label = "time"
prep_p.xaxis.formatter=DatetimeTickFormatter()

prep_p.yaxis.axis_label = "prep pressure (mbar)"

prep_r = prep_p.line(x='x', y='prep_pressure', source=plot_source)

## microscope pressure plot

micro_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=plot_width, plot_height=plot_height)
# micro_p.toolbar.active_scroll = wheel_zoom

micro_p.y_range.range_padding=0

micro_p.xaxis.axis_label = "time"
micro_p.xaxis.formatter=DatetimeTickFormatter()

micro_p.yaxis.axis_label = "microscope pressure (mbar)"

micro_r = micro_p.line(x='x', y='microscope_pressure', source=plot_source)

### historical range plot:

hist_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=int(2.5*plot_width), plot_height=plot_height)
# hist_p.toolbar.active_scroll = wheel_zoom

hist_p.y_range.range_padding=0

hist_p.xaxis.axis_label = "time"
hist_p.xaxis.formatter=DatetimeTickFormatter()

hist_p.yaxis.axis_label = "pressure (mbar)"

hist_r = hist_p.line(x='x', y='y', source=historical_source)


## remove zero's for plotting:
    
for aa, ii, jj, kk in zip(read_pressures.source.data['x'], read_pressures.source.data['LL_pressure'], 
                            read_pressures.source.data['prep_pressure'], 
                            read_pressures.source.data['microscope_pressure']):
    if ii <= 0. or math.isnan(ii):
        try:
            ii = plot_source.data['LL_pressure'][-1]
        except:
            ii = 10
    if jj <= 0. or math.isnan(jj):
        try:
            jj = plot_source.data['prep_pressure'][-1]
        except:    
            jj = 10
    if kk <= 0. or math.isnan(kk):
        try:
            kk = plot_source.data['microscope_pressure'][-1]
        except:
            kk = 10
    plot_source.stream(dict(x=[aa], LL_pressure=[ii], prep_pressure=[jj], microscope_pressure=[kk]), rollover=read_rollover_interval)
    

@gen.coroutine
def plot_update():
    global timer_zero
    try:
        temp_time = (dt.timestamp(dt.now())+3600)*1e3
        # LL_temp = read_pressures.source.data['LL_pressure'][-1]
        LL_temp = read_pressures.current_LL
        if LL_temp == 0. or math.isnan(LL_temp):
            try:
                LL_temp = plot_source.data['LL_pressure'][-1]
            except:
                LL_temp = 10
            LL_display.value = "gauge problem"
        else:
            LL_display.value = str(LL_temp)
        # prep_temp = read_pressures.source.data['prep_pressure'][-1]
        prep_temp = read_pressures.current_prep
        if prep_temp == 0. or math.isnan(prep_temp):
            try:
                prep_temp = plot_source.data['prep_pressure'][-1]
            except:
                prep_temp = 10
            prep_display.value = "gauge problem"
        else:
            prep_display.value = str(prep_temp)
        # micro_temp = read_pressures.source.data['microscope_pressure'][-1]
        micro_temp = read_pressures.current_micro
        if micro_temp == 0. or math.isnan(micro_temp):
            try:
                micro_temp = plot_source.data['microscope_pressure'][-1]
            except:
                micro_temp = 10
            micro_display.value = "gauge problem"
        else:
            micro_display.value = str(micro_temp)
        
        plot_source.stream(dict(x=[temp_time],
            LL_pressure=[LL_temp],
            prep_pressure=[prep_temp],
            microscope_pressure=[micro_temp]), 
            rollover=rollover_interval)
            


            
    except:
        print("something wrong in main")
        pass
    t1 = time.time()
    timer_display.value = str(datetime.timedelta(seconds=int(round(t1-timer_zero))))
        
@gen.coroutine
def log_history_update(channel_selected, start_date, end_date):

    try:
        f = open(log_filename)

        historical_source.data = dict(x=[], y=[])
        
        for line in iter(f):
            ts, pressure = str.split(line, '\t', 1)
            LL_temp, pressure = str.split(pressure, '\t', 1)
            prep_temp, micro_temp = str.split(pressure, '\t', 1)
            ts = dt.strptime(ts, "%Y-%m-%d %H:%M:%S")
            LL_temp = float(LL_temp)
            if LL_temp == 0. or math.isnan(LL_temp):
                try:
                    LL_temp = historical_source.data['y'][-1]
                except:
                    LL_temp = 10
            prep_temp = float(prep_temp)
            if prep_temp == 0. or math.isnan(prep_temp):
                try:
                    prep_temp = historical_source.data['y'][-1]
                except:
                    prep_temp = 10
            micro_temp = float(micro_temp)
            if micro_temp == 0. or math.isnan(micro_temp):
                try:
                    micro_temp = historical_source.data['y'][-1]
                except:
                    micro_temp = 10
            if ts > dt.strptime(start_date, "%Y-%m-%d") and ts < dt.strptime(end_date, "%Y-%m-%d"):
                if channel_selected == "LL_pressure" and LL_temp != 0.:
                    historical_source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[LL_temp]))
                if channel_selected == "prep_pressure" and prep_temp != 0.:
                    historical_source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[prep_temp]))
                if channel_selected == "microscope_pressure" and micro_temp != 0.:
                    historical_source.stream(dict(x=[(dt.timestamp(ts)+3600)*1e3], y=[micro_temp]))
        f.close()
    except:
        print("something wrong with log file read")
        pass


LL_display = TextInput(title="LL pressure", value=" ")
prep_display = TextInput(title="prep pressure", value=" ")
micro_display = TextInput(title="microscope pressure", value=" ")

LL_d = PreText

### widgets for historical data display:

widget_width = 150


menu = [("LL pressure", "LL_pressure"), ("prep pressure", "prep_pressure"), ("microscope", "microscope_pressure")]
channel_selection = Dropdown(label="select channel", button_type="success", menu=menu, width=widget_width)

# start_date_widget = DatePicker(title="start date", min_date=dt(2017,1,1), max_date=dt.now(), value=dt(dt.now().year,1,1))
# end_date_widget = DatePicker(title="end date", min_date=dt(2017,1,1), max_date=dt.now(), value=dt(dt.now().year,1,1))
start_date_widget = TextInput(title="start date (YYYY-MM-DD)", value=str(dt.now()-timedelta(days=1))[:10], width=widget_width)
end_date_widget = TextInput(title="end date (YYYY-MM-DD)", value=str(dt.now()+timedelta(days=1))[:10], width=widget_width)
update_hist_data = Button(label="update plot", width=widget_width)

timer_display = TextInput(title="timer", value=" ")
reset_button = Button(label="reset", button_type="default")


##callback to update history plot:
def update_plot():
    log_history_update(channel_selection.value, start_date_widget.value, end_date_widget.value)
    return
update_hist_data.on_click(update_plot)



def change_title(attr):
    channel_selection.label = channel_selection.value
    return
channel_selection.on_click(change_title)

@gen.coroutine
def reset_timer():
    global timer_zero
    timer_zero = time.time()

### seed initial values:
channel_selection.value = "LL_pressure" ## seed initial value
change_title("title")
update_plot()
global timer_zero
timer_zero = time.time()

reset_button.on_click(reset_timer)

# hist_layout = column(hist_p, column(channel_selection, start_date_widget, end_date_widget, update_hist_data))

hist_widgets = widgetbox(channel_selection, start_date_widget, end_date_widget, update_hist_data)

LL_plots = column(LL_display, LL_p)
prep_plots = column(prep_display, prep_p)
micro_plots = column(micro_display, micro_p)

# l = layout([LL_display, prep_display, micro_display], [LL_p, prep_p, micro_p], [hist_p, hist_widgets]) # sizing_mode='scale_width')
l = layout([LL_plots, prep_plots, micro_plots, column(timer_display, reset_button)], [hist_p, hist_widgets]) #, sizing_mode='scale_width')
            
# l2 = column(l, hist_layout)
curdoc().add_root(l)

curdoc().title = "JT pressure status"
curdoc().add_periodic_callback(plot_update, update_interval)


    
