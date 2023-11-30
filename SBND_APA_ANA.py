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


def FEMB_CHK(fembdata, rms_f = False):
    RAW_C = RAW_CONV()
    chn_rmss = []
    chn_peds = []
    chn_pkps = []
    chn_pkns = []
    chn_waves = []
    chn_avg_waves = []

    for adata in fembdata:
        chn_data, feed_loc, chn_peakp, chn_peakn = RAW_C.raw_conv_peak(adata)
        for achn in range(len(chn_data)):
            achn_ped = []
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
            chn_pkps.append(apeakp)
            chn_pkns.append(apeakn)
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
    return (True, "pass-", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves,chn_avg_waves])


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

def FEMB_PLOT(results, fn="./"):
    chn_rmss = results[2][0]
    chn_peds = results[2][1]
    chn_pkps = results[2][2]
    chn_pkns = results[2][3]
    chn_wfs =  results[2][4]

    import matplotlib.pyplot as plt
    ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 2), (0, 1), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((2, 2), (1, 1), colspan=1, rowspan=1)
    chns = range(len(chn_rmss))
    FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Pedestal", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
    FEMB_SUB_PLOT(ax3, chns, chn_pkps, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax3, chns, chn_peds, title="Pedestal", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
    FEMB_SUB_PLOT(ax3, chns, chn_pkns, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='g', marker='.')
    for chni in range(128):
        ts = 100 if (len(chn_wfs[chni]) > 100) else len(chn_wfs[chni])
        x = (np.arange(ts)) * 0.5
        y = chn_wfs[chni][0:ts]
        FEMB_SUB_PLOT(ax4, x, y, title="Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))
 
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#    plt.savefig(fn)
    plt.show()
    plt.close()

def SBND_MAP():
    fn_map = "./SBND_mapping.csv"
    dec_chn = []
    with open (fn_map, 'r') as fp:
        for cl in fp:
            if "\n" in cl:
                cl = cl.replace("\n", "")
            tmp = cl.split(",")
            x = []
            for i in tmp:
                x.append(i.replace(" ", ""))
            dec_chn.append(x)
    dec_chn = dec_chn[1:]
    return dec_chn

#fp = """/Users/shanshangao/Downloads/tmp/LD1128/WIB10.226.34.41FEMB1_Time2023_11_28_09_25_28.bin"""
#with open (fp, "rb") as fs:
#    raw = pickle.load(fs)
#RAW_C = RAW_CONV()
#results = FEMB_CHK(raw)
#FEMB_PLOT(results)
  
def SBND_ANA(rawdir):
    fns = []
    for root, dirs, files in os.walk(rawdir):
        for fn in files:
            if ("WIB_" in fn) and ("FEMB_" in fn) and (".bin" in fn):
                wibloc = fn.find("FEMB_")
                crateno = int(fn[wibloc-2])
                ptbno = int(fn[wibloc-1])
                fembno = int(fn[wibloc+5])
                fns.append([crateno, ptbno, fembno, rawdir + fn])
        break
    
    dec_chn = SBND_MAP()
    lendec = len(dec_chn)
    for df in fns:
        print ("Analyze: ", df)
        crateno = df[0]
        wibno   = df[1]
        fembno  = df[2]
        with open (df[3], "rb") as fs:
            raw = pickle.load(fs)
        results = FEMB_CHK(raw)
        chn_rmss = results[2][0]
        chn_peds = results[2][1]
        chn_pkps = results[2][2]
        chn_pkns = results[2][3]
        chn_wfs =  results[2][4]
        chn_avgwfs =  results[2][5]
    
        for i in range(lendec):
            if (int(dec_chn[i][5]) == crateno) and (int(dec_chn[i][6]) == wibno ) and (int(dec_chn[i][7]) == fembno ) :
                decch = int(dec_chn[i][8])
                dec_chn[i].append(chn_rmss[decch])
                dec_chn[i].append(chn_peds[decch])
                dec_chn[i].append(chn_pkps[decch])
                dec_chn[i].append(chn_pkns[decch])
         
    fr =rawdir + "test_results"+".result" 
    with open(fr, 'wb') as f:
        pickle.dump(dec_chn, f)

    return None
#    for chn in range(1,1986):
#        for i in range(lendec):
#            if (int(dec_chn[i][10]) == chn):
#                if (int(dec_chn[i][5]) <= 2): #west apa
#                    if len(dec_chn[i])>12:
#                        if "U" in dec_chn[i][9]:
#                            w_urmss.append( dec_chn[i][12])
#                            w_upeds.append( dec_chn[i][13])
#                            w_upkps.append( dec_chn[i][14])
#                            w_upkns.append( dec_chn[i][15])
#                        if "V" in dec_chn[i][9]:
#                            w_vrmss.append( dec_chn[i][12])
#                            w_vpeds.append( dec_chn[i][13])
#                            w_vpkps.append( dec_chn[i][14])
#                            w_vpkns.append( dec_chn[i][15])
#                        if "Y" in dec_chn[i][9]:
#                            w_yrmss.append( dec_chn[i][12])
#                            w_ypeds.append( dec_chn[i][13])
#                            w_ypkps.append( dec_chn[i][14])
#                            w_ypkns.append( dec_chn[i][15])
#                else:#east apa
#                    if len(dec_chn[i])>12:
#                        if "U" in dec_chn[i][9]:
#                            e_urmss.append( dec_chn[i][12])
#                            e_upeds.append( dec_chn[i][13])
#                            e_upkps.append( dec_chn[i][14])
#                            e_upkns.append( dec_chn[i][15])
#                        if "V" in dec_chn[i][9]:
#                            e_vrmss.append( dec_chn[i][12])
#                            e_vpeds.append( dec_chn[i][13])
#                            e_vpkps.append( dec_chn[i][14])
#                            e_vpkns.append( dec_chn[i][15])
#                        if "Y" in dec_chn[i][9]:
#                            e_yrmss.append( dec_chn[i][12])
#                            e_ypeds.append( dec_chn[i][13])
#                            e_ypkps.append( dec_chn[i][14])
#                            e_ypkns.append( dec_chn[i][15])
#    #    break
#    result = [
#                ["EU", e_urmss, e_upeds, e_upkps, e_upkns],
#                ["Ev", e_vrmss, e_vpeds, e_vpkps, e_vpkns],
#                ["EY", e_yrmss, e_ypeds, e_ypkps, e_ypkns],
#                ["WU", w_urmss, w_upeds, w_upkps, w_upkns],
#                ["Wv", w_vrmss, w_vpeds, w_vpkps, w_vpkns],
#                ["WY", w_yrmss, w_ypeds, w_ypkps, w_ypkns]
             ]
def d_dec_plt(d, plt, n=-4):
    wireno = d[10]
    wirev = d[n]
    if "U" in d[9]:
        if wireno == 1:
            plt.scatter(wireno, wirev, color='b', label = "U" )
        else:
            plt.scatter(wireno, wirev, color='b'  )
    if "V" in d[9]:
        if wireno == 1:
            plt.scatter(wireno, wirev, color='g', label = "V" )
        else:
            plt.scatter(wireno, wirev, color='g'  )
    if "Y" in d[9]:
        if wireno == 1:
            plt.scatter(wireno, wirev, color='g', label = "Y" )
        else:
            plt.scatter(wireno, wirev, color='g'  )
    
def dis_plot(dec_chn, fdir, title="EAST APA: RMS Distribution @ (14mV/fC, 2.0us)", fn = "EAST_APA_RMS.png"):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10,6))
    plt.rcParams.update({'font.size': 18})
    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
    for d in dec_chn:
        if d[5] > 2 :#Crate no, EAST APA
            d_dec_plt(d, plt, n=-4)
    plt.ylim((0,10))
    plt.xlim((0,6000))
    plt.ylabel ("RMS / bit")
    plt.xlabel ("Channel NO.")
    plt.title (title)
    plt.legend()
    plt.grid()
    ffig = fdir + fn
#    plt.savefig(ffig)
    plt.show()
    plt.close()



rawdir = """/Users/shanshangao/Downloads/tmp/1129/CHK/LD1/"""
fr =rawdir + "test_results"+".result" 
if (os.path.isfile(fr)):
    with open(fr, 'rb') as f:
        result = pickle.load(f)
    pass
else:
    result = SBND_ANA(rawdir)

dis_plot(dec_chn=result, fdir=rawdir, title="EAST APA: RMS Distribution @ (14mV/fC, 2.0us)", fn = "EAST_APA_RMS.png"):

exit()

    
print (len(w_urmss),len(w_vrmss), len(w_yrmss), len(e_urmss),len(e_vrmss), len(e_yrmss)  )
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(10,6))
x = np.arange(len(w_urmss)) + 1
plt.plot(x, w_urmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_urmss)) + 1
plt.plot(x, e_urmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_vrmss)) + 1
plt.plot(x, w_vrmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_vrmss)) + 1
plt.plot(x, e_vrmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_yrmss)) + 1
plt.plot(x, w_yrmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_yrmss)) + 1
plt.plot(x, e_yrmss)
plt.show()
plt.close()
exit()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_upeds)) + 1
plt.plot(x, w_upeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_upeds)) + 1
plt.plot(x, e_upeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_vpeds)) + 1
plt.plot(x, w_vpeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_vpeds)) + 1
plt.plot(x, e_vpeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_ypeds)) + 1
plt.plot(x, w_ypeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_ypeds)) + 1
plt.plot(x, e_ypeds)
plt.show()
plt.close()


#    femb_date = qc_list[4]
#    print(qc_pf)
#    print(env)
#    print(femb_id)
#    print(femb_rerun_f)
#    print(femb_date)

  #  break
    


