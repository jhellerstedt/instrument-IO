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
import pickle

from datetime import datetime as dt
import pytz

from bokeh.models import ColumnDataSource


## 2021-12-17 libraries to pull temperatures from Julian's firebase server
import firebase_admin
from firebase_admin import credentials, db




## set the log filename as a string
log_filename = "/home/jack/instrument-IO/G80_pressure_logging/G80_temperature_log.txt"
# log_filename = os.getcwd() + "/" + log_filename
print(log_filename)


### if the update_interval callback is 2000 ms or less, too fast for reading the pressure gauge
update_interval = 5000 ## ms
data_interval = 3 ## minutes; spacing between data points in total_axis "buffer"
total_axis_hours = 24 ## total hours to keep in bokeh plot
log_interval = 10 ## minutes interval to write data points to log file

log_interval = log_interval * 60
total_axis_hours = np.multiply(total_axis_hours,3.6e6) ## hours to ms
data_interval = data_interval * 60 * 1e3 ## minutes to ms

global rollover_interval
rollover_interval = int(np.floor(np.divide(total_axis_hours, data_interval)))

source = ColumnDataSource(data=dict(x=[], T_stm=[], T_cryo=[]))

#### populate plot with old data if possible:
try:
    os.environ['TZ'] = 'UTC+0' #'Australia/Melbourne' ## Melbourne is UTC+10
    time.tzset()
    f = open(log_filename)
    for line in iter(f):
        ts, temperature = str.split(line, '\t', 1)
        T_stm, T_cryo = str.split(temperature, '\t', 1)

        ts = dt.strptime(ts, "%Y-%m-%d %H:%M:%S")
        T_stm = float(T_stm)
        if math.isnan(T_stm):
            T_stm = 350.
        T_cryo = float(T_cryo)
        if math.isnan(T_cryo):
            prep_temp = 350.
        source.stream(dict(x=[(dt.timestamp(ts))*1e3], T_stm=[T_stm], T_cryo=[T_cryo]), rollover=rollover_interval)
    f.close()
except:
    print("log file read issues")
    pass    
    
global t0, t0_two, first_run
t0 = time.time()
t0_two = time.time()

first_run = True

global current_T_stm, current_T_cryo
current_T_stm = 0
current_T_cryo = 0


def update():
    global t0, t0_two, rollover_interval, first_run, log_interval, current_LL, current_prep, current_micro
    
    while True:
        # print("sup reading gauges")
        os.environ['TZ'] = 'UTC+0' #'Australia/Melbourne' ## Melbourne is UTC+10
        time.tzset()
        time.sleep(update_interval/1e3) ##convert ms to s
        try:
            ### replace with the function call to read the instrument you want   
            ### 2021-12-17 this json credential/ this URL are from Julian's firebase thing.
            cred = credentials.Certificate('jc.json')
            firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://g80live-default-rtdb.firebaseio.com/'
                })
            
            current_T_stm  = float(db.reference('stmTemp').get())
            current_T_cryo = float(db.reference('cryoTemp').get())
            
            ts = dt.now(tz=pytz.timezone('Australia/Melbourne'))
            ts = str(ts)
            ts = ts[:19]
            
            t1 = time.time()
            
            ## write current temperature to disk
         
            temperature_dict = {}
            temperature_dict['T_stm'] = current_T_stm
            temperature_dict['T_cryo'] = current_T_cryo
            with open("/home/jack/instrument-IO/G80_pressure_logging/current_temperature.p", 'wb') as f:
                pickle.dump(temperature_dict, f)
            
            if t1 - t0_two > data_interval * 1e-3 or first_run == True:
                ## the 1e3 is some weird bokeh correction, maybe a ms/ns problem
                source.stream(dict(x=[(dt.timestamp(dt.strptime(ts, "%Y-%m-%d %H:%M:%S")))*1e3], T_stm=[T_stm], T_cryo=[T_cryo]), rollover=rollover_interval)
                t0_two = t1
  
            
            if t1 - t0 > log_interval or first_run == True:  ## take a log point every log_interval minutes    
                first_run = False
                log = open(log_filename, 'a')
                log.write(ts + "\t" + str(current_T_stm) + "\t" + str(current_T_cryo) + "\n")
                log.close()
                t0 = t1
                ## limit log file length to ~1 month = ~4500 lines @ 10min intervals
                with open(log_filename, 'r') as f:
                    content = f.readlines()
                if len(content) > 4500: ## number of lines of log to keep
                    with open(log_filename, 'w') as f:
                        f.writelines(content[1:])
                       
        except:
            print("something wrong with FIREBASE")
            continue
            
