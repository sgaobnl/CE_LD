# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Sun Mar 10 22:09:41 2024
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
import numpy as np

import sys 
import os
import string
import struct
import codecs
import datetime
import time
import pickle
from shutil import copyfile
import operator
import pandas as pd

def d_dec_plt(dec_chn, n=1):
    euvals = []
    evvals = []
    eyvals = []
    wuvals = []
    wvvals = []
    wyvals = []

    for d in dec_chn:
        wireno = int(d[10])
        if (len(d)>=16):
            wirev = d[11+n]
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

def RMS_Mean(vals):
        #remove results form abnormal channels
        vals = np.asarray(vals)
        subvals = vals[vals > 0]
        subvals = sorted(subvals)
        subvals = subvals[50:-50] 
        meanv = np.mean(subvals)
        stdv = np.std(subvals)
        return meanv, stdv, len(subvals)

def RMS_ANA(dec_chn, ns=[5]):
    for n in ns:
        euvals, evvals, eyvals, wuvals, wvvals, wyvals = d_dec_plt(dec_chn, n=n)

        chns, vals=list(zip(*sorted(euvals, key=operator.itemgetter(0))))
        eu = RMS_Mean(vals)
        chns, vals=list(zip(*sorted(wuvals, key=operator.itemgetter(0))))
        wu = RMS_Mean(vals)

        chns, vals=list(zip(*sorted(evvals, key=operator.itemgetter(0))))
        ev = RMS_Mean(vals)
        chns, vals=list(zip(*sorted(wvvals, key=operator.itemgetter(0))))
        wv = RMS_Mean(vals)

        chns, vals=list(zip(*sorted(eyvals, key=operator.itemgetter(0))))
        ey = RMS_Mean(vals)
        chns, vals=list(zip(*sorted(wyvals, key=operator.itemgetter(0))))
        wy = RMS_Mean(vals)
        break
    return eu, wu, ev, wv, ey, wy


def RMS_TS_ANA(rmsts, result_dir, rms_flg=True):
    lrmsts = []
    for x in rmsts:
        if x[1] is None:
            pass
        elif x[4] != 0:
            pass
        elif x[5] != 0:
            pass
        elif rms_flg and (x[3] != 0):
            pass
        else:
            lrmsts.append(x)
    rmsts = lrmsts
    rmsts=sorted(rmsts, key=operator.itemgetter(0))
    ts = []
    eums = []
    euss = []
    evms = []
    evss = []
    eyms = []
    eyss = []
    wums = []
    wuss = []
    wvms = []
    wvss = []
    wyms = []
    wyss = []

    for x in rmsts:
        if (x[1][0][2]>1000) and (x[1][1][2]>1000) and (x[1][2][2]>1000) and (x[1][3][2]>1000) and (x[1][4][2]>1000) and (x[1][5][2]>1000):
            tstr = datetime.datetime.fromtimestamp(x[0]).strftime("%Y-%m-%d %H:%M:%S")
            ts.append(tstr)
            eums.append(x[1][0][0])
            euss.append(x[1][0][1])
            wums.append(x[1][1][0])
            wuss.append(x[1][1][1])
            evms.append(x[1][2][0])
            evss.append(x[1][2][1])
            wvms.append(x[1][3][0])
            wvss.append(x[1][3][1])
            eyms.append(x[1][4][0])
            eyss.append(x[1][4][1])
            wyms.append(x[1][5][0])
            wyss.append(x[1][5][1])
        else:
            continue
    #t0 = int(ts[0]//(3600*24))*3600*24
    #t0 = int(ts[0])
    #t0str = datetime.datetime.fromtimestamp(t0).strftime("%Y-%m-%d %H:%M:%S")
    #t0str = t0str[0:11] + "00:00:00"

    #datex = datetime.datetime.strptime(t0str, "%Y-%m-%d %H:%M:%S")
    #t0 = datex.timestamp()
    #ts = (np.array(ts)-t0)/3600.0

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12,9))
    plt.rcParams.update({'font.size': 12})
    ax1 = plt.subplot(311)
    ax2 = plt.subplot(312)
    ax3 = plt.subplot(313)
    ts = pd.to_datetime(ts)

    ax1.errorbar(ts, eums, euss, marker='o', color='C1', label="EAST APA U")
    ax1.errorbar(ts, wums, wuss, marker='o', color='C4', label="WEST APA U")
    ax2.errorbar(ts, evms, evss, marker='s', color='C2', label="EAST APA V")
    ax2.errorbar(ts, wvms, wvss, marker='s', color='C5', label="WEST APA V")
    ax3.errorbar(ts, eyms, eyss, marker='x', color='C3', label="EAST APA Y")
    ax3.errorbar(ts, wyms, wyss, marker='x', color='C6', label="WEST APA Y")
    #for x in range(0, int(np.max(ts))+24, 24):
    #    ax1.vlines(x, 0, 5, linestyles='dashed',color='k')
    #    ax2.vlines(x, 0, 5, linestyles='dashed',color='k')
    #    ax3.vlines(x, 0, 5, linestyles='dashed',color='k')
    ax1.set_ylim((0,5))
    ax2.set_ylim((0,5))
    ax3.set_ylim((0,5))
    ax1.set_ylabel ("RMS noise / bit")
    ax2.set_ylabel ("RMS noise / bit")
    ax3.set_ylabel ("RMS noise / bit")
    #ax3.set_xlabel ("Time / hour")
    #ax1.text(0,4.5,t0str)
    #ax2.text(0,4.5,t0str)
    #ax3.text(0,4.5,t0str)
    #ax1.grid(axis='y')
    #ax2.grid(axis='y')
    #ax3.grid(axis='y')
    ax1.grid()
    ax2.grid()
    ax3.grid()

    ax1.legend()
    ax2.legend()
    ax3.legend()
    plt.gcf().autofmt_xdate()
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    #plt.show()
    if rms_flg:
        plt.savefig(result_dir + "RMS_vs_Time.png")
    else:
        plt.savefig(result_dir + "RMS_Cali_vs_Time.png")
    plt.close()

#rawdir = """/Users/shanshangao/Downloads/SBND_LD/LD_result/"""
rawdir = """/scratch_local/SBND_Installation/data/commissioning/LD_result/"""
#rawdir = """/Users/shanshangao/Downloads/SBND_LD/LD/LD_result/"""

result_dir = rawdir 

frmsts = result_dir + "RMSvsTime.rms"
if (os.path.isfile(frmsts)):
    with open (frmsts, "rb") as fs:
        rmsts = pickle.load(fs)
else:
    rmsts = []

for root, dirs, files in os.walk(rawdir):
    #for fn in files[0:20]:
    for fn in files:
        if ("LD_2024_" in fn) and (".png" not in fn) and (".ld" in fn[-3:]):
            rn = rawdir + fn
            if len(rmsts) != 0:
                flg = False
                for rmst in rmsts:
                    if (rmst[2] == rn):
                        flg = True
                        break
                if flg == True:
                    continue
            print (rn)
            logdate=fn[3:3+19]
            datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
            x = datex.timestamp()
            if (os.path.isfile(rn)):
                if (int(fn[8:10]) == 2) and (int(fn[11:13])<16): 
                    with open(rn, 'rb') as f:
                        result = pickle.load(f)
                        res = RMS_ANA(dec_chn=result, ns=[5])
                        rmsts.append([x,res, rn, 0, 0, 0])
                else:
                    with open(rn, 'rb') as f:
                        result = pickle.load(f)
                        dec_chn = result
                        sts = 0
                        femb_tst_sel = 0
                        tst_wfm_gen_mode = 0
                        for i in range(len(dec_chn)):
                            if len(dec_chn[i]) > 20:
                                sts = dec_chn[i][0-17]
                                sg0 = dec_chn[i][0-17+2]
                                sg1 = dec_chn[i][0-17+3]
                                st0 = dec_chn[i][0-17+4]
                                st1 = dec_chn[i][0-17+5]
                                femb_tst_sel = dec_chn[i][9-31]
                                tst_wfm_gen_mode = dec_chn[i][4-41]
                                break
                
                    if (femb_tst_sel == 0 ) and (tst_wfm_gen_mode == 0) and (sg0 == 0) and (sg1 == 1) and (st0 == 1) and (st1 == 1):
                        res = RMS_ANA(dec_chn=result, ns=[5])
                        rmsts.append([x,res, rn, sts, femb_tst_sel, tst_wfm_gen_mode])
                    else:
                        rmsts.append([x,None, rn, sts, femb_tst_sel, tst_wfm_gen_mode])

with open (frmsts, "wb") as fs:
    pickle.dump(rmsts, fs)

import copy
RMS_TS_ANA(copy.deepcopy(rmsts), result_dir, rms_flg=True)
RMS_TS_ANA(copy.deepcopy(rmsts), result_dir, rms_flg=False)


