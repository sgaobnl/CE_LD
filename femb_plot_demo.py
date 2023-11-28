# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/28/2023 4:54:27 PM
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


import matplotlib.pyplot as plt
fp = """/Users/shanshangao/Downloads/tmp/LD1128/WIB10.226.34.41FEMB0_Time2023_11_28_09_25_28.bin"""
with open (fp, "rb") as fs:
    raw = pickle.load(fs)
RAW_C = RAW_CONV()

def FEMB_CHK(fembdata):
    chn_rmss = []
    chn_peds = []
    chn_pkps = []
    chn_pkns = []
    chn_waves = []
    chn_avg_waves = []

    for adata in fembdata:
        print (len(fembdata), len(adata))
        chn_data, feed_loc, chn_peakp, chn_peakn = RAW_C.raw_conv_peak(adata)
        for achn in range(len(chn_data)):
            achn_ped = []
            rms_f = False
            if (rms_f):
                achn_ped += chn_data[achn] 
            else:
                for af in range(len(feed_loc[0:-2])):
                    achn_ped += chn_data[achn][feed_loc[af]+100: feed_loc[af+1]-100 ] 
            arms = np.std(achn_ped)
            aped = int(np.mean(achn_ped))
            apeakp = int(np.mean(chn_peakp[achn]))
            apeakn = int(np.mean(chn_peakn[achn]))
            chn_rmss.append(arms)
            chn_peds.append(aped)
            chn_pkps.append(abs(apeakp-aped))
            chn_pkns.append(abs(apeakn-aped))
            chn_waves.append( chn_data[achn][feed_loc[0]: feed_loc[1]] )
            avg_cnt = len(feed_loc)-2

            avg_wave = np.array(chn_data[achn][feed_loc[0]: feed_loc[0] + 100]) 
            for i in (1, avg_cnt,1):
                #avg_wave += np.array(chn_data[achn][feed_loc[i]: feed_loc[i+1]]) 
                avg_wave += np.array(chn_data[achn][feed_loc[i]: feed_loc[i]+100]) 
            avg_wave = avg_wave/avg_cnt
            chn_avg_waves.append(avg_wave)
    ana_err_code = ""
    rms_mean = np.mean(chn_rmss)

    for gi in range(8): 
        ped_mean = np.mean(chn_peds[gi*16 : (gi+1)*16])
        pkp_mean = np.mean(chn_pkps[gi*16 : (gi+1)*16])
        pkn_mean = np.mean(chn_pkns[gi*16 : (gi+1)*16])
        ped_thr= 30 
    return (True, "PASS-", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves,chn_avg_waves])

results = FEMB_CHK(raw)

def FEMB_SUB_PLOT(ax, x, y, title, xlabel, ylabel, color='b', marker='.', atwinx=False, ylabel_twx = "", e=None):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (atwinx):
        ax.errorbar(x,y,e, marker=marker, color=color)
        y_min = int(np.min(y))-1000
        y_max = int(np.max(y))+1000
        ax.set_ylim([y_min, y_max])
        ax2 = ax.twinx()
        ax2.set_ylabel(ylabel_twx)
        ax2.set_ylim([int((y_min/16384.0)*2048), int((y_max/16384.0)*2048)])
    else:
        ax.plot(x,y, marker=marker, color=color)

def FEMB_PLOT(results)
    import matplotlib.pyplot as plt
    ax1 = plt.subplot2grid((4, 2), (2, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((4, 2), (3, 0), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((4, 2), (2, 1), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((4, 2), (3, 1), colspan=1, rowspan=1)
    chns = range(len(chn_rmss))
    FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Pedestal", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
    FEMB_SUB_PLOT(ax3, chns, chn_pkps, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax3, chns, chn_pkns, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='g', marker='.')
    FEMB_SUB_PLOT(ax4, x, y, title="Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))
    FEMB_SUB_PLOT(ax4, x, y2, title="Averaging Waveform Overlap ", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))
    
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.savefig(fn)
    plt.close()

  
