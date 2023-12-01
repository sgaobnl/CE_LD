# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 12/1/2023 10:19:54 AM
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
import operator


def FEMB_CHK(fembdata, rms_f = False, fs="./"):
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

    result = (True, "pass-", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves,chn_avg_waves])
    FEMB_PLOT(result, fn=fs.replace(".bin", ".png"))
    return result


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
#    fn = rawdir +  
    plt.savefig(fn)
#    plt.show()
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
        results = FEMB_CHK(raw, rms_f=False, fs=df[3])
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
    fr =rawdir + "test_results"+".csv" 
    with open (fr, 'w') as fp:
        top_row = "APA,Crate,FEMB_SN,POSITION,WIB_CONNECTION,Crate_No,WIB_no,WIB_FEMB_LOC,FEMB_CH,Wire_type,Wire_No,,RMS Noise, Pedestal, Pulse_Pos_Peak, Pulse_Neg_Peak"
        fp.write( top_row + "\n")
        for x in dec_chn:
                fp.write(",".join(str(i) for i in x) +  "," + "\n")
    return dec_chn

def d_dec_plt(dec_chn, n=-4):
    euvals = []
    evvals = []
    eyvals = []
    wuvals = []
    wvvals = []
    wyvals = []

    for d in dec_chn:
        wireno = int(d[10])
        if (len(d)==16):
            wirev = d[n]
        else:
            wirev = -1
        if int (d[5]) > 2:
            if "U" in d[9]:
                euvals.append([wireno,wirev])
            if "V" in d[9]:
                evvals.append([wireno,wirev])
            if "Y" in d[9]:
                eyvals.append([wireno,wirev])
        else:
            if "U" in d[9]:
                wuvals.append([wireno,wirev])
            if "V" in d[9]:
                wvvals.append([wireno,wirev])
            if "Y" in d[9]:
                wyvals.append([wireno,wirev])

    return euvals, evvals, eyvals, wuvals, wvvals, wyvals
    
def dis_plot(dec_chn, fdir, title = "RMS Noise Distribution", fn = "SBND_APA_RMS_DIS.png", ns=[-4], ylim=[-2,10]):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12,6))
    plt.rcParams.update({'font.size': 12})
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)

    ax1.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    ax1.text(1000, 0, "U", color='b')
    ax1.text(3000, 0, "V", color='g')
    ax1.text(5000, 0, "Y", color='r')
    ax1.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
    ax2.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    ax2.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
    ax2.text(1000, 0, "U", color='b')
    ax2.text(3000, 0, "V", color='g')
    ax2.text(5000, 0, "Y", color='r')


    for n in ns:
        euvals, evvals, eyvals, wuvals, wvvals, wyvals = d_dec_plt(dec_chn, n=n)

        chns, vals=list(zip(*sorted(euvals, key=operator.itemgetter(0))))
        ax1.plot(chns, vals, color='m', marker='.', mfc='b', mec='b', label = "U" )
        chns, vals=list(zip(*sorted(wuvals, key=operator.itemgetter(0))))
        ax2.plot(chns, vals, color='m', marker='.', mfc='b', mec='b', label = "U" )

        chns, vals=list(zip(*sorted(evvals, key=operator.itemgetter(0))))
        ax1.plot(np.array(chns)+1984, vals, color='m', marker='.', mfc='g', mec='g',  label = "V" )
        chns, vals=list(zip(*sorted(wvvals, key=operator.itemgetter(0))))
        ax2.plot(np.array(chns)+1984, vals, color='m', marker='.', mfc='g', mec='g',  label = "V" )

        chns, vals=list(zip(*sorted(eyvals, key=operator.itemgetter(0))))
        ax1.plot(np.array(chns)+1984*2, vals, color='m', marker='.', mfc='r', mec='r',  label = "Y" )
        chns, vals=list(zip(*sorted(wyvals, key=operator.itemgetter(0))))
        ax2.plot(np.array(chns)+1984*2, vals, color='m', marker='.', mfc='r', mec='r',  label = "Y" )
    ax1.set_ylim((ylim))
    ax1.set_xlim((0,6000))
    ax1.set_ylabel ("RMS / bit")
    ax1.set_xlabel ("Channel NO.")
    ax1.set_title ("EAST APA: " + title)
#    ax1.legend()
    ax1.grid()

    ax2.set_ylim((ylim))
    ax2.set_xlim((0,6000))
    ax2.set_ylabel ("RMS / bit")
    ax2.set_xlabel ("Channel NO.")
    ax2.set_title ("WEST APA: " + title)
#    ax2.legend()
    ax2.grid()


    ffig = fdir + fn
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.show()
    plt.close()



rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/1129/CHK/LD1/"""
fr =rawdir + "test_results"+".result" 
if (os.path.isfile(fr)):
    with open(fr, 'rb') as f:
        result = pickle.load(f)
    pass
else:
    result = SBND_ANA(rawdir)

dis_plot(dec_chn=result, fdir=rawdir, title = "RMS Noise Distribution", fn = "SBND_APA_RMS_DIS.png", ns=[-4], ylim=[-2,8])
dis_plot(dec_chn=result, fdir=rawdir, title = "Pulse Response Distribution", fn = "SBND_APA_RMS_DIS.png", ns=[-3,-2,-1], ylim=[-100,4000])


    

