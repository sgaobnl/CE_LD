# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 3/25/2025 3:43:06 PM
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
from raw_convertor_28chn import RAW_CONV
import pickle
from shutil import copyfile

rawdir = """D:/uFEMB/Rawdata/"""
fn = rawdir + "Rawdata.bin"

with open (fn, "rb") as fs:
    rawdata = pickle.load(fs)

rc = RAW_CONV()

chn_data = rc.raw_conv(raw_data=rawdata)

import matplotlib.pyplot as plt
for i in range(32):
    print (hex(chn_data[i][0]))
#exit()
for i in range(32):
    fig = plt.figure(figsize=(8,6))
    plt.rcParams.update({'font.size': 18})
    plt.plot(chn_data[i] )
    plt.show()
    plt.close()

