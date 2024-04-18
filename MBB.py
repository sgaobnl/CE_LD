# -*- coding: utf-8 -*-
"""
File Name: Main.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 1/13/2018 3:05:03 PM
Last modified: Thu Apr 18 14:46:39 2024
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

import os
import sys
import copy
from datetime import datetime
import numpy as np
import time
from timeit import default_timer as timer

###############################################################################
from cls_udp import CLS_UDP
wib= CLS_UDP()

logs = []

if True
    wib.UDP_IP = "10.226.34.50" 
    while (1):
        tmp = input("Start DAQ (1), Stop DAQ(2), Timestamp Reset (3), Exit(other number)  = ")
        tmp = int(tmp)
        if tmp > 3 or tmp < 1:
            exit()
        else:
            if tmp == 1: #bit3 set to 0 --> 1 --> 0
                adr = 1
                val = wib.read_reg_wib(adr)
                val = val&0xf7
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                val = val|0x08
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                val = val&0xf7
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                print (adr, wib.read_reg_wib(adr))
            elif tmp == 2: #bit2 set to 0 --> 1 --> 0
                adr = 1
                val = wib.read_reg_wib(adr)
                val = val&0xfb
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                val = val|0x04
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                val = val&0xfb
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                print (adr, wib.read_reg_wib(adr))
            elif tmp == 3: #bit1 set to 0 --> 1 --> 0
                adr = 1
                val = wib.read_reg_wib(adr)
                val = val&0xfd
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                val = val|0x02
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                val = val&0xfd
                wib.write_reg_wib(adr, val)
                wib.write_reg_wib(adr, val)
                print (adr, wib.read_reg_wib(adr))

if False
    while (1):
        tmp = input("adr, data, w/r = ")
        if tmp[0] == "N":
            break
        else:
            tmpi = tmp.find(",")
            tmp2 = tmpi + 1 + tmp[tmpi+1:].find(",")
            adr = int(tmp[0:tmpi])
            data = int(tmp[tmpi+1:tmp2])
            wr_en = (tmp[tmp2:])
        for lastip in ["50"]:
            #wib.UDP_IP = "192.168.121." +  lastip
            wib.UDP_IP = "10.226.34." +  lastip
            print (wib.read_reg_wib(adr))
            if ("w" in wr_en) or ("W" in wr_en):
                wib.write_reg_wib(adr, data)
                time.sleep(1)
                print (adr, wib.read_reg_wib(adr))
 
#for i in range(1):
#    #for lastip in ["209"]:
#    for lastip in ["11"]:
#        wib.UDP_IP = "192.168.121." +  lastip
#        #wib.UDP_IP = "131.225.150." +  lastip
#        print wib.UDP_IP
#        time.sleep(1)
#        print wib.read_reg_wib(1)
#        print wib.read_reg_wib(2)
#        wib.write_reg_wib(1, 2)
#        time.sleep(1)
#        print wib.read_reg_wib(1)
#        wib.write_reg_wib(1, 0)
#        time.sleep(1)
#        print wib.read_reg_wib(1)
#
