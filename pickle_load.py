# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Thu Feb 15 11:58:55 2024
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

fn = """/Users/shanshangao/Downloads/SBND_LD/LD_2024_02_14_09_13_41/WIB_10_226_34_46FEMB_1_Time2024_02_14_09_14_02.femb"""
with open (fn, "rb") as fs:
    raw = pickle.load(fs)

for i in range(len(raw)):
    print ("Reg %x, Value %x"%(raw[i][0], raw[i][1]))


