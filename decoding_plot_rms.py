# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 3/31/2025 6:01:56 PM
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

#rawdir = """D:/uFEMB/Rawdata/T3_CH1_47_300mV_X/"""
#fn = rawdir + "Rawdata.bin"
#fn = rawdir + "RMS_SG01_SG11_ST01_ST11_Rawdata.bin"
rc = RAW_CONV()

t1cap = [180,184,162,157,161,256,258,264,271,281,277,286,270,270,274]
t2cap = [181,185,162,164,164,262,264,269,271,278,277,287,269,274,273]
t3cap = [176,167,154,156,156,207,202,203,199,199,194,192,188,184,186]

t1 = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[] ]
t2 = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[] ]
t3 = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[] ]

fnt2t1 = """D:/uFEMB/Rawdata/T2T1RTRMS/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
#fnt2t1 = """D:/uFEMB/Rawdata/LNRMS_T2T1/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fn = fnt2t1
chn_data=[]
with open (fn, "rb") as fs:
    rawdata = pickle.load(fs)
for chip in range(2):
    chn_data += rc.raw_conv(raw_data=rawdata[chip])

for pi in range(15):
    t1[pi] = chn_data[14-pi]
for pi in range(3,15,1):
    t2[pi] = chn_data[16+pi-3]

fnt3t2 = """D:/uFEMB/Rawdata/T3T2RTRMS/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
#fnt3t2 = """D:/uFEMB/Rawdata/LNRMS_T3T2/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fn = fnt3t2
chn_data=[]
with open (fn, "rb") as fs:
    rawdata = pickle.load(fs)
for chip in range(2):
    chn_data += rc.raw_conv(raw_data=rawdata[chip])
for pi in range(3):
    t2[pi] = chn_data[11-pi]
for pi in range(0,15,1):
    t3[pi] = chn_data[16+pi]

t1.reverse()
t2.reverse()
t3.reverse()

t1rms = []
t2rms = []
t3rms = []
for pi in range(15):
    t1rms.append(np.std(t1[pi]))
    t2rms.append(np.std(t2[pi]))
    t3rms.append(np.std(t3[pi]))



###############################################################
LNt1 = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[] ]
LNt2 = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[] ]
LNt3 = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[] ]

#fnt2t1 = """D:/uFEMB/Rawdata/T2T1RTRMS/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fnt2t1 = """D:/uFEMB/Rawdata/LNRMS_T2T1/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fn = fnt2t1
chn_data=[]
with open (fn, "rb") as fs:
    rawdata = pickle.load(fs)
for chip in range(2):
    chn_data += rc.raw_conv(raw_data=rawdata[chip])

for pi in range(15):
    LNt1[pi] = chn_data[14-pi]
for pi in range(3,15,1):
    LNt2[pi] = chn_data[16+pi-3]

#fnt3t2 = """D:/uFEMB/Rawdata/T3T2RTRMS/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fnt3t2 = """D:/uFEMB/Rawdata/LNRMS_T3T2/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fnt3t2 = """D:/uFEMB/Rawdata/LNRMS_T3T2_v1/RMS_SG00_SG10_ST00_ST10_Rawdata.bin"""
fn = fnt3t2
chn_data=[]
with open (fn, "rb") as fs:
    rawdata = pickle.load(fs)
for chip in range(2):
    chn_data += rc.raw_conv(raw_data=rawdata[chip])
for pi in range(3):
    LNt2[pi] = chn_data[11-pi]
for pi in range(0,15,1):
    LNt3[pi] = chn_data[16+pi]

LNt1.reverse()
LNt2.reverse()
LNt3.reverse()

LNt1rms = []
LNt2rms = []
LNt3rms = []
for pi in range(15):
    LNt1rms.append(np.std(LNt1[pi]))
    LNt2rms.append(np.std(LNt2[pi]))
    LNt3rms.append(np.std(LNt3[pi]))


#RMS
#import matplotlib.pyplot as plt
##fig=plt.figure(figsize=(16,9))
#fig, ax = plt.subplots()
#p1,=ax.plot(t1rms, color = 'r', marker='s', label="RT_T1_RMS")
##p1,=ax.plot(t2rms, color = 'r', marker='s', label="RT_T2_RMS")
##p1,=ax.plot(t3rms, color = 'r', marker='s', label="RT_T3_RMS")
#
#p3,=ax.plot(LNt1rms, color = 'b', marker='>', label="LN_T1_RMS")
##p3,=ax.plot(LNt2rms, color = 'b', marker='>', label="LN_T2_RMS")
##p3,=ax.plot(LNt3rms, color = 'b', marker='>', label="LN_T3_RMS")
#
#
#ax.set(xlim=(-1, 16), ylim=(0,12), xlabel="Electrode pad order #", ylabel="ADC RMS Noise / bit")

import matplotlib.pyplot as plt
#fig=plt.figure(figsize=(16,9))
fig, ax = plt.subplots()
#p1,=ax.plot(np.array(t1rms)*175, color = 'r', marker='s', label="RT_T1_ENC")
#p1,=ax.plot(np.array(t2rms)*175, color = 'r', marker='s', label="RT_T2_ENC")
p1,=ax.plot(np.array(t3rms)*175, color = 'r', marker='s', label="RT_T3_ENC")

#p3,=ax.plot(np.array(LNt1rms)*175, color = 'b', marker='>', label="LN_T1_ENC")
#p3,=ax.plot(np.array(LNt2rms)*175, color = 'b', marker='>', label="LN_T2_ENC")
p3,=ax.plot(np.array(LNt3rms)*175, color = 'b', marker='>', label="LN_T3_ENC")

ax.set(xlim=(-1, 16), ylim=(0,12*175), xlabel="Electrode pad order #", ylabel="ENC / e-")



ax.grid()

tw = ax.twinx()

#p2,=tw.plot(t1cap, color = 'g', marker='o', label="T1_Cap")
#p2,=tw.plot(t2cap, color = 'g', marker='o', label="T2_Cap")
p2,=tw.plot(t3cap, color = 'g', marker='o', label="T3_Cap")


tw.set( ylim=(0, 300),  ylabel="Capacitance / pF")

plt.legend(handles=[p1,p3, p2 ], loc=2)
plt.show()
plt.close()

exit()
rc = RAW_CONV()

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


pd = 1000
chn_data_avgs = []

import matplotlib.pyplot as plt
#for ch in [224 ,25, 26, 27, 28, 29, 30, 31]:
for ch in range(32):
    for avgi in range(500):
        if avgi == 0:
            chn_data_avg = np.array(chn_data[ch][0:pd])
        else:
            chn_data_avg = chn_data_avg + np.array(chn_data[ch][avgi*pd:(avgi+1)*pd])
    chn_data_avg = chn_data_avg/500
    chn_data_avg = chn_data_avg - np.mean(chn_data_avg)
        
    plt.plot(chn_data_avg,marker='.' )
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

