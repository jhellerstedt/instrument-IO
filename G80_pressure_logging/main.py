#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 17:29:28 2016

@author: jack
"""

import os
import time
import numpy as np
import math

import traceback

from tornado import gen

import datetime
from datetime import datetime as dt
from datetime import timedelta
import pytz

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, WheelZoomTool, Column, Select
from bokeh.models.widgets import TextInput, Button, PreText
from bokeh.layouts import column, layout #, widgetbox

import read_pressures

from read_pressures import update_interval, log_filename
from read_pressures import rollover_interval as read_rollover_interval

import read_temperatures
from read_temperatures import temperature_log_filename


total_axis_hours = 24
total_axis_hours = np.multiply(total_axis_hours,3.6e6) ## hours to ms
rollover_interval = int(np.floor(np.divide(total_axis_hours, update_interval)))

plot_source = ColumnDataSource(data=dict(x=[], LL_pressure=[], prep_pressure=[], microscope_pressure=[], T_stm=[], T_cryo=[]))

historical_source = ColumnDataSource(data=dict(x=[], y=[]))


TOOLS="pan,wheel_zoom,box_zoom,reset,box_select,save"
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


## microscope temperatures plot

temperature_plot = figure(tools=TOOLS, y_axis_type='linear', x_axis_type='datetime', plot_width=plot_width, plot_height=plot_height)
temperature_plot.xaxis.axis_label = 'time'
temperature_plot.xaxis.formatter=DatetimeTickFormatter()

temperature_plot.yaxis.axis_label = 'temperature (K)'
temperature_plot_dict = {}
for temp, color in zip(['T_stm', 'T_cryo'], ['red', 'blue']):
    temperature_plot_dict[temp] = temperature_plot.line(x='x', y=temp, color=color, source=plot_source)



### historical range plot:

hist_p = figure(tools=TOOLS, y_axis_type="log", x_axis_type="datetime", plot_width=int(2.5*plot_width), plot_height=plot_height)
# hist_p.toolbar.active_scroll = wheel_zoom

hist_p.y_range.range_padding=0

hist_p.xaxis.axis_label = "time"
hist_p.xaxis.formatter=DatetimeTickFormatter()

hist_p.yaxis.axis_label = "pressure (mbar)"

hist_r = hist_p.line(x='x', y='y', source=historical_source)


## remove zero's for plotting:
    
for aa, ii, jj, kk, ttstm, ttcryo in zip(read_pressures.source.data['x'], read_pressures.source.data['LL_pressure'], 
                            read_pressures.source.data['prep_pressure'], 
                            read_pressures.source.data['microscope_pressure'],
                            read_temperatures.source.data['T_stm'],
                            read_temperatures.source.data['T_cryo']):
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
    plot_source.stream(dict(x=[aa], LL_pressure=[ii], prep_pressure=[jj], microscope_pressure=[kk], T_stm=[ttstm], T_cryo=[ttcryo]), rollover=read_rollover_interval)
    

@gen.coroutine
def plot_update():
    global timer_zero
    
    os.environ['TZ'] = 'UTC+0' ## Melbourne is UTC+10
    time.tzset()
    ts = dt.now(tz=pytz.timezone('Australia/Melbourne'))
    ts = str(ts)
    ts = ts[:19]
    
    try:
        LL_temp = read_pressures.current_LL
        if LL_temp == 0. or math.isnan(LL_temp):
            try:
                LL_temp = plot_source.data['LL_pressure'][-1]
            except:
                LL_temp = 10
            LL_display.value = "gauge problem"
        else:
            LL_display.value = str(LL_temp)
        prep_temp = read_pressures.current_prep
        if prep_temp == 0. or math.isnan(prep_temp):
            try:
                prep_temp = plot_source.data['prep_pressure'][-1]
            except:
                prep_temp = 10
            prep_display.value = "gauge problem"
        else:
            prep_display.value = str(prep_temp)
        micro_temp = read_pressures.current_micro
        if micro_temp == 0. or math.isnan(micro_temp):
            try:
                micro_temp = plot_source.data['microscope_pressure'][-1]
            except:
                micro_temp = 10
            micro_display.value = "gauge problem"
        else:
            micro_display.value = str(micro_temp)
       
            
        try:
            # T_stm_display.value = plot_source.data['T_stm'][-1]
            T_stm_display.value = str('{0:3.1f}'.format(read_temperatures.current_T_stm))
        except:
            T_stm_display.value = 'T_stm problem'
            traceback.print_exc()
        try:
            # T_cryo_display.value = plot_source.data['T_cryo'][-1]
            T_cryo_display.value = str('{0:3.1f}'.format(read_temperatures.current_T_cryo))
        except:
            T_cryo_display.value = 'T_cryo problem'
            traceback.print_exc()
        
        plot_source.stream(dict(x=[(dt.timestamp(dt.strptime(ts, "%Y-%m-%d %H:%M:%S")))*1e3],
                                LL_pressure=[LL_temp],
                                prep_pressure=[prep_temp],
                                microscope_pressure=[micro_temp],
                                T_stm=[read_temperatures.current_T_stm],
                                T_cryo=[read_temperatures.current_T_cryo]
                                ),
                           rollover=rollover_interval)
            
    except:
        traceback.print_exc()
        pass
    t1 = time.time()
    timer_display.value = str(datetime.timedelta(seconds=int(round(t1-timer_zero))))
    
    datetime_display.value = dt.fromtimestamp(dt.timestamp(dt.strptime(ts, "%Y-%m-%d %H:%M:%S"))).strftime('%c')
        
@gen.coroutine
def log_history_update(channel_selected, start_date, end_date):

    try:
        os.environ['TZ'] = 'UTC+0' ## Melbourne is UTC+10
        time.tzset()
        
        historical_source.data = dict(x=[], y=[])
        
        if channel_selected in ["LL_pressure", "prep_pressure", "microscope_pressure"]:
            
            hist_p.yaxis.axis_label = 'pressure (mbar)'
            
            f = open(log_filename)
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
                        historical_source.stream(dict(x=[(dt.timestamp(ts))*1e3], y=[LL_temp]))
                    if channel_selected == "prep_pressure" and prep_temp != 0.:
                        historical_source.stream(dict(x=[(dt.timestamp(ts))*1e3], y=[prep_temp]))
                    if channel_selected == "microscope_pressure" and micro_temp != 0.:
                        historical_source.stream(dict(x=[(dt.timestamp(ts))*1e3], y=[micro_temp]))
            f.close()
        
        if channel_selected in ["T_stm", "T_cryo"]:
            
            hist_p.yaxis.axis_label = 'Temperature (K)'
            
            f = open(temperature_log_filename)
            for line in iter(f):
                ts, temperature = str.split(line, '\t', 1)
                T_stm, T_cryo = str.split(temperature, '\t', 1)
                ts = dt.strptime(ts, "%Y-%m-%d %H:%M:%S")
                
                T_stm = float(T_stm)
                if T_stm == 0. or math.isnan(T_stm):
                    try:
                        T_stm = historical_source.data['y'][-1]
                    except:
                        T_stm = 550
                
                T_cryo = float(T_cryo)
                if T_cryo == 0. or math.isnan(T_cryo):
                    try:
                        T_cryo = historical_source.data['y'][-1]
                    except:
                        T_cryo = 550
                if ts > dt.strptime(start_date, "%Y-%m-%d") and ts < dt.strptime(end_date, "%Y-%m-%d"):
                    if channel_selected == "T_stm" and T_stm != 0.:
                        historical_source.stream(dict(x=[(dt.timestamp(ts))*1e3], y=[T_stm]))
                    if channel_selected == "T_cryo" and T_cryo != 0.:
                        historical_source.stream(dict(x=[(dt.timestamp(ts))*1e3], y=[T_cryo]))
            f.close()
    except:
        traceback.print_exc()
        pass


LL_display = TextInput(title="LL pressure", value=" ")
prep_display = TextInput(title="prep pressure", value=" ")
micro_display = TextInput(title="microscope pressure", value=" ")

T_cryo_display = TextInput(title='T_cryo', value=" ")
T_stm_display = TextInput(title='T_stm', value=" ")

LL_d = PreText

### widgets for historical data display:

widget_width = 150


options = ["LL_pressure", "prep_pressure", "microscope_pressure", "T_stm", "T_cryo"]
channel_selection = Select(title="select channel", value="prep_pressure", options=options, width=widget_width)

# start_date_widget = DatePicker(title="start date", min_date=dt(2017,1,1), max_date=dt.now(), value=dt(dt.now().year,1,1))
# end_date_widget = DatePicker(title="end date", min_date=dt(2017,1,1), max_date=dt.now(), value=dt(dt.now().year,1,1))
start_date_widget = TextInput(title="start date (YYYY-MM-DD)", value=str(dt.now()-timedelta(days=1))[:10], width=widget_width)
end_date_widget = TextInput(title="end date (YYYY-MM-DD)", value=str(dt.now()+timedelta(days=1))[:10], width=widget_width)
update_hist_data = Button(label="update plot", width=widget_width)

timer_display = TextInput(title="timer", value=" ")
reset_button = Button(label="reset", button_type="default")

## add diagnostic date time
datetime_display = TextInput(title="timestamp", value=" ")


##callback to update history plot:
def update_plot(attr):
    log_history_update(channel_selection.value, start_date_widget.value, end_date_widget.value)
    return

update_hist_data.on_click(update_plot)

def update_val(attr, old, new):
    update_plot(attr)
    return
    
channel_selection.on_change('value', update_val)


@gen.coroutine
def reset_timer():
    global timer_zero
    timer_zero = time.time()


global timer_zero
timer_zero = time.time()

reset_button.on_click(reset_timer)

# hist_layout = column(hist_p, column(channel_selection, start_date_widget, end_date_widget, update_hist_data))

hist_widgets = Column(channel_selection, start_date_widget, end_date_widget, update_hist_data)

LL_plots = column(LL_display, LL_p)
prep_plots = column(prep_display, prep_p)
micro_plots = column(micro_display, micro_p)
temperature_plots = column(T_stm_display, T_cryo_display, temperature_plot)

# l = layout([LL_display, prep_display, micro_display], [LL_p, prep_p, micro_p], [hist_p, hist_widgets]) # sizing_mode='scale_width')
l = layout([LL_plots, prep_plots, micro_plots, temperature_plots, column(timer_display, reset_button, datetime_display)], [hist_p, hist_widgets]) #, sizing_mode='scale_width')
            
# l2 = column(l, hist_layout)
curdoc().add_root(l)

curdoc().title = "G80 pressure status"
curdoc().add_periodic_callback(plot_update, update_interval)


    
