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
import string
import time
from datetime import datetime
import struct
import codecs
from cls_config import CLS_CONFIG
from raw_convertor import RAW_CONV
import pickle
from shutil import copyfile

LD = CLS_CONFIG()
LD.savedir = "/home/nfs/sgao/SBND_Installation/data/LD1128/"
LD.ldflg=True
LD.WIB_IPs = [
              #"10.226.34.11",
              #"10.226.34.12",
              #"10.226.34.13",
              #"10.226.34.14",
              #"10.226.34.15",
              #"10.226.34.16", 
              #"10.226.34.21",
              #"10.226.34.22",
              #"10.226.34.23",
              #"10.226.34.24",
              #"10.226.34.25",
              #"10.226.34.26", 
              #"10.226.34.31",
              #"10.226.34.32",
              #"10.226.34.33",
              #"10.226.34.34",
              #"10.226.34.35",
              #"10.226.34.36",
              "10.226.34.41",
              "10.226.34.42",
              "10.226.34.43",
              "10.226.34.44",
              "10.226.34.45",
              "10.226.34.46" ]
for wib_ip in LD.WIB_IPs:
    print (wib_ip)
    if ".16" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".26" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".36" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".46" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".34.34" in wib_ip:
        LD.act_fembs[wib_ip] = [False, True, True, True]
    else:
        LD.act_fembs[wib_ip] = [True, True, True, True]

cfglog = ""
LD.TPC_UDPACQ(cfglog)

print ("Done")

