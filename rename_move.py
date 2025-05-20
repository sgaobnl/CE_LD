# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/13/2025 9:36:23 AM
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
import pickle
import shutil
import numpy as np

rootdir = """G:/SiPM/"""
srcdir =  """G:/bak/"""
for root, dirs, files in os.walk(srcdir):
    break

anafs = []
bakfs = []
for rawd in files:
    if "Anaata_" in rawd:
        anafs.append(rawd)
    elif "Bakata_" in rawd:
        bakfs.append(rawd)
#Anaata_20250509_14_38
for fn in anafs:
    sdir = fn[0:21]
    dstdir = rootdir + sdir + "/"
    if not os.path.exists(dstdir):
        try:
            os.makedirs(dstdir)
        except OSError:
            print ("Error to create folder %s"%dstdir)
            sys.exit()
    srcf = srcdir + fn
    shutil.move(srcf, dstdir)
    
for fn in bakfs:
    sdir = fn[0:21]
    dstdir = rootdir + sdir + "/"
    if not os.path.exists(dstdir):
        try:
            os.makedirs(dstdir)
        except OSError:
            print ("Error to create folder %s"%dstdir)
            sys.exit()
    srcf = srcdir + fn
    shutil.move(srcf, dstdir)


