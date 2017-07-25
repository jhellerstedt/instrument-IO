#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 17:29:28 2016

@author: jack
"""

import threading
from threading import Thread

import multiprocessing

from tornado import gen

import read_temps

global run_measurement
run_measurement = False

def on_server_loaded(server_context):
    print("called on_server_loaded")
    t = Thread(target=read_temps.update, args=())
    t.setDaemon(True)
    t.start()
    # print(threading.get_ident())
    return
    
def on_server_unloaded(server_context):
    # read_pressures.LL_gauge.TPG_close_serial('\dev\ttyUSB2')
    # read_pressures.prep_gauge.VACOM_close_serial('\dev\ttyUSB0')
    # read_pressures.micro_gauge.VACOM_close_serial('\dev\ttyUSB1')
    # t.join()
    return