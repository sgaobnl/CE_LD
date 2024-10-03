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

wib.UDP_IP = "10.226.34.50" 
print ("MBB IP address ",wib.UDP_IP)
while (1):
    thiscrate = input("Crate number (1-4) = ")
    thiscrate = int(thiscrate)
    thiswib = input("WIB number (1-6) = ")
    thiswib = int(thiswib)
    if thiscrate > 4 or thiscrate < 1 or thiswib > 6 or thiswib < 1:
        exit()
    else:
        mbb_adr=0x04
        val = wib.read_reg_wib(mbb_adr)
        print ("MBB address ",hex(mbb_adr)," = ",val)
        ptc_data_adr=0x02
        ptc_crate_adr=thiscrate
        mbb_adr=0x04

                #val = val&0xf7
                #wib.write_reg_wib(adr, val)


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
