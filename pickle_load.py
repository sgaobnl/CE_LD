# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Fri Feb 16 14:36:38 2024
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
import pickle
from shutil import copyfile
import operator

fn = """/Users/shanshangao/Downloads/SBND_LD/LD_2024_02_16_12_42_33/WIB_10_226_34_46FEMB_0_Time2024_02_16_12_42_56.femb"""
fn = """/Users/shanshangao/Downloads/SBND_LD/LD_2024_02_16_12_42_33/WIB_10_226_34_45FEMB_0_Time2024_02_16_12_42_55.wib"""
with open (fn, "rb") as fs:
    raw = pickle.load(fs)

for i in range(len(raw)):
    print ("Reg %x, Value %x"%(raw[i][0], raw[i][1]))


