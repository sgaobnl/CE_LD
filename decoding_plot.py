# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 3/31/2025 5:25:42 PM
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
from raw_convertor import RAW_CONV
import pickle
from shutil import copyfile
import numpy as np
from fft_chn import chn_fft

rawdir = """D:/uFEMB/Rawdata/T3_CH1_47_300mV_X/"""
fn = rawdir + "Rawdata.bin"
fn = rawdir + "RMS_SG01_SG11_ST01_ST11_Rawdata.bin"
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_1000mV_T1_CH5_47_200us//RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_70mV_T1_CH2_47_200us/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_70mV_T1_CH1_47_200us_a/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_150mV_T1_CH1_47/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_500mV_T1_CH1_47/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_2000mV_T1_CH1_47/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_5000mV_T1_CH1_47/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""

fn = """D:/uFEMB/Rawdata/T2T1RTRMS_70mV_T1_CH8_47_200us/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_1000mV_T1_CH2_47_200us/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""


fn = """D:/uFEMB/Rawdata/T2T1RTRMS_500mV_T1_CH1_47_200ns/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_70mV_T1_CH1_47_200ns/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_1000mV_T1_CH1_47_200ns/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_2000mV_T1_CH1_47_200ns/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_5000mV_T1_CH1_47_200ns/RMS_SG01_SG11_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB/Rawdata/T2T1RTRMS_5000mV_T1_CH1_47_200ns/RMS_SG01_SG11_ST01_ST11_Rawdata.bin"""
fn = """D:/uFEMB\Rawdata/ASICDAC20/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB\Rawdata/ASICDAC05/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fn = """D:/uFEMB\Rawdata/LNSGP05/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""

with open (fn, "rb") as fs:
    rawdata = pickle.load(fs)

rc = RAW_CONV()
chn_data = []

for chip in range(2):
    chn_data += rc.raw_conv(raw_data=rawdata[chip])


#import matplotlib.pyplot as plt
#rmss = []
#for i in range(32):
#    print (np.std(chn_data[i]), i, np.mean(chn_data[i]))
#    rmss.append(np.std(chn_data[i]))
#plt.plot(rmss,marker='.' )
#plt.show()
#plt.close()
#exit()


pd = 500
chn_data_avgs = []

import matplotlib.pyplot as plt
#for ch in [224 ,25, 26, 27, 28, 29, 30, 31]:
#for ch in range(32):
for ch in range(1,5):
    chn_data[ch] = chn_data[ch][100:]
    for avgi in range(500):
        if avgi == 0:
            chn_data_avg = np.array(chn_data[ch][0:pd])
        else:
            chn_data_avg = chn_data_avg + np.array(chn_data[ch][avgi*pd:(avgi+1)*pd])
    chn_data_avg = chn_data_avg/500
    chn_data_avg = chn_data_avg - np.mean(chn_data_avg)
        
    plt.plot(chn_data_avg,marker='.', label="CH%d"%ch )
plt.grid()
plt.legend(loc=1)
plt.show()
plt.close()

#import matplotlib.pyplot as plt
#rmss = []
#for i in range(32):
#    print (np.std(chn_data[i]), i, np.mean(chn_data[i]))
#    rmss.append(np.std(chn_data[i]))
#plt.plot(rmss,marker='.' )
#plt.show()
#plt.close()
#for i in range(32):
##for i in [30]:
#    fig = plt.figure(figsize=(8,6))
#    plt.rcParams.update({'font.size': 18})
##    plt.plot(chn_data[i], label="Ch%d"%i )
#    print (len(chn_data[i]))
##    f,p = chn_fft(chn_data[i], fft_s=5000 )
#    plt.plot(f,p)
#    plt.legend()
#    plt.show()

