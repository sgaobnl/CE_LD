# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Wed Jan 31 21:29:19 2024
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
import string
import time
from datetime import datetime
import struct
import codecs
from cls_config import CLS_CONFIG
from raw_convertor import RAW_CONV
import pickle
from shutil import copyfile
from setdatadir import savedir

LD = CLS_CONFIG()
LD.val=200
runtime =  datetime.now().strftime('%Y_%m_%d_%H_%M_%S') 
LD.savedir = savedir + "/LD_" + runtime + "/"

if (os.path.exists(LD.savedir)):
    pass
else:
    try:
        os.makedirs(LD.savedir)
    except OSError:
        print ("Error to create folder %s"%LD.savedir)
        sys.exit()
print("Save data in "+LD.savedir)

LD.ldflg=True
LD.UDP.MultiPort = True
LD.WIB_IPs = [
              "10.226.34.11",
              "10.226.34.12",
              "10.226.34.13",
              "10.226.34.14",
              "10.226.34.15",
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
for wib_ip in LD.WIB_IPs:
    print (wib_ip)
    if ".16" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
#    elif ".14" in wib_ip:
#        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".26" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".36" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".46" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
#    elif ".34.34" in wib_ip:
#        LD.act_fembs[wib_ip] = [False, True, True, True]
    else:
        LD.act_fembs[wib_ip] = [True, True, True, True]

cfglog = ""
LD.TPC_UDPACQ(cfglog)

print ("Done")

