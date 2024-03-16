# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/28/2023 4:53:22 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
import numpy as np
#import scipy as sp
#import pylab as pl

import sys 
import os
import time
from datetime import datetime
from cls_config import CLS_CONFIG

LD = CLS_CONFIG()
LD.ldflg=True
LD.WIB_IPs = [
              "10.226.34.11",
              "10.226.34.12",
              "10.226.34.13",
              "10.226.34.14",
              "10.226.34.15",
#              "10.226.34.16"
              "10.226.34.16", 
              "10.226.34.21",
              "10.226.34.22",
              "10.226.34.23",
              "10.226.34.24",
              "10.226.34.25",
              "10.226.34.26", 
              "10.226.34.31",
              "10.226.34.32",
              "10.226.34.33",
              "10.226.34.34",
              "10.226.34.35",
              "10.226.34.36",
              "10.226.34.41",
              "10.226.34.42",
              "10.226.34.43",
              "10.226.34.44",
              "10.226.34.45",
              "10.226.34.46"
              ]

LD.UDP.MultiPort = True
for wib_ip in LD.WIB_IPs:
    LD.UDP.UDP_IP = wib_ip
    LD.UDP.write_reg_wib(0x14, 0xCF)
    val = LD.UDP.read_reg_wib(0x14)
    print (wib_ip, val)
time.sleep(1)
for wib_ip in LD.WIB_IPs:
    LD.UDP.UDP_IP = wib_ip
    LD.UDP.write_reg_wib(0x14, 0x100)
    val = LD.UDP.read_reg_wib(0x14)
    print (wib_ip, val)
time.sleep(1)
for wib_ip in LD.WIB_IPs:
    LD.UDP.UDP_IP = wib_ip
    LD.UDP.write_reg_wib(0x14, 0x000)
    val = LD.UDP.read_reg_wib(0x14)
    print (wib_ip, val)
time.sleep(1)

exit()




for wib_ip in LD.WIB_IPs:
    LD.UDP.UDP_IP = wib_ip
    if mp == 1:
        LD.UDP.UDP_PORT_RREGRESP = 32000 + 0x10 + int(wib_ip[-2:])
        val = LD.UDP.read_reg_wib(0xFF)
        print (hex(val))
        #val = LD.UDP.read_reg_wib(0x08)
        #print (hex(val))
        #val = LD.UDP.read_reg_femb(0, 0x101)
        print (hex(val))
    elif mp == 0:
        LD.UDP.UDP_PORT_RREGRESP = 32002
        val = LD.UDP.read_reg_wib(0xFF)
        print (hex(val))

print ("Done")

