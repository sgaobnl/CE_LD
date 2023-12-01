# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 12/1/2023 11:38:37 AM
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

from femb_qc import FEMB_QC
qc= FEMB_QC()
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/1129/CHK/"""
fn = rawdir + "WIB10_226_34_11_FEMB0_0_00FE_1101111000_Time2023_11_29_10_49_47.bin"

qc.databkdir = rawdir
with open (fn, "rb") as fs:
    qc_data = pickle.load(fs)

if ("_FEMB" in fn) and (".bin" in fn):
    wibloc = fn.find("_FEMB")
    crateno = int(fn[wibloc-2])
    ptbno = int(fn[wibloc-1])
    fembno = int(fn[wibloc+5])

FEMB_infos = qc.FEMB_CHKOUT_Input(crateno,ptbno)
tmp = []
for x in FEMB_infos:
    if fembno == int(x[x.find("WIBslot")+7]):
        tmp.append(x)

FEMB_infos = tmp
print (FEMB_infos)


testcode = 1
qcs = qc.FEMB_CHK_ANA(FEMB_infos, [qc_data], pwr_i=testcode)
qc.FEMB_PLOT(pwr_int_f = False)
