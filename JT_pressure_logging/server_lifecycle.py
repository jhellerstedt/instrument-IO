#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 17:29:28 2016

@author: jack
"""


from threading import Thread

import read_pressures

def on_server_loaded(server_context):
    t = Thread(target=read_pressures.update, args=())
    t.setDaemon(True)
    t.start()
    
def on_server_unloaded(server_context):
    LL_gauge.TPG_close_serial('\dev\ttyUSB2')
    prep_gauge.VACOM_close_serial('\dev\ttyUSB0')
    micro_gauge.VACOM_close_serial('\dev\ttyUSB1')