# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Mon Feb 12 15:19:26 2024
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


def RMS_TS_ANA(rmsts, result_dir):
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
        ts.append(x[0])
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
    #t0 = int(ts[0]//(3600*24))*3600*24
    t0 = int(ts[0])
    t0str = datetime.datetime.fromtimestamp(t0).strftime("%Y-%m-%d %H:%M:%S")
    t0str = t0str[0:11] + "00:00:00"

    datex = datetime.datetime.strptime(t0str, "%Y-%m-%d %H:%M:%S")
    t0 = datex.timestamp()
    ts = (np.array(ts)-t0)/3600.0

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12,9))
    plt.rcParams.update({'font.size': 12})
    ax1 = plt.subplot(311)
    ax2 = plt.subplot(312)
    ax3 = plt.subplot(313)

    ax1.errorbar(ts, eums, euss, marker='o', color='C1', label="EAST APA U")
    ax1.errorbar(ts, wums, wuss, marker='o', color='C4', label="WEST APA U")
    ax2.errorbar(ts, evms, evss, marker='s', color='C2', label="EAST APA V")
    ax2.errorbar(ts, wvms, wvss, marker='s', color='C5', label="WEST APA V")
    ax3.errorbar(ts, eyms, eyss, marker='x', color='C3', label="EAST APA Y")
    ax3.errorbar(ts, wyms, wyss, marker='x', color='C6', label="WEST APA Y")
    for x in range(0, int(np.max(ts))+24, 24):
        ax1.vlines(x, 0, 5, linestyles='dashed',color='k')
        ax2.vlines(x, 0, 5, linestyles='dashed',color='k')
        ax3.vlines(x, 0, 5, linestyles='dashed',color='k')
    ax1.set_ylim((0,5))
    ax2.set_ylim((0,5))
    ax3.set_ylim((0,5))
    ax1.set_ylabel ("RMS noise / bit")
    ax2.set_ylabel ("RMS noise / bit")
    ax3.set_ylabel ("RMS noise / bit")
    ax3.set_xlabel ("Time / hour")
    ax1.text(0,4.5,t0str)
    ax2.text(0,4.5,t0str)
    ax3.text(0,4.5,t0str)
    ax1.grid(axis='y')
    ax2.grid(axis='y')
    ax3.grid(axis='y')
    ax1.legend()
    ax2.legend()
    ax3.legend()
    plt.savefig(result_dir + "RMS_vs_Time.png")
    plt.close()

#rawdir = """/Users/shanshangao/Downloads/SBND_LD/LD_result/"""
rawdir = """/scratch_local/SBND_Installation/data/commissioning/"""

result_dir = rawdir + "LD_result/"

rmsts = []
for root, dirs, files in os.walk(rawdir):
    #for fn in files[0:20]:
    for fn in files:
        if ("LD_2024_" in fn) and (".png" not in fn):
            rn = rawdir + fn
            print (rn)
            logdate=fn[3:3+19]
            datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
            x = datex.timestamp()
            if (os.path.isfile(rn)):
                with open(rn, 'rb') as f:
                    result = pickle.load(f)
                res = RMS_ANA(dec_chn=result, ns=[5])
            rmsts.append([x,res])

RMS_TS_ANA(rmsts, result_dir)


