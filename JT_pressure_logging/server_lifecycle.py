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

import read_pressures

def on_server_loaded(server_context):
    # t = Thread(target=read_pressures.update, args=())
    # t.setDaemon(True)
    # t.start()
    t = multiprocessing.Process(target=read_pressures.update, args=())
    jobs.append(t)
    t.start()
    return
    
def on_server_unloaded(server_context):
    # read_pressures.LL_gauge.TPG_close_serial('\dev\ttyUSB2')
    # read_pressures.prep_gauge.VACOM_close_serial('\dev\ttyUSB0')
    # read_pressures.micro_gauge.VACOM_close_serial('\dev\ttyUSB1')
    t.join()
    return