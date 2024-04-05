# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Thu Mar 28 23:52:10 2024
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
    plt.show()
    if rms_flg:
        plt.savefig(result_dir + "RMS_vs_Time.png")
    else:
        plt.savefig(result_dir + "RMS_Cali_vs_Time.png")
    plt.close()

def TempRMS_TS_ANA(rmsts, result_dir, temps, rms_flg=True):
    logdate = "2024_02_05_20_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttime_start = datex.timestamp()    
    
    logdate = "2024_02_12_14_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemin = datex.timestamp()    
    logdate = "2024_02_12_20_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemax = datex.timestamp()    
    del_zone1 = [ttimemin, ttimemax] 
    
    logdate = "2024_02_13_15_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemin = datex.timestamp()    
    logdate = "2024_02_13_18_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemax = datex.timestamp()    
    del_zone2 = [ttimemin, ttimemax] 
    
    logdate = "2024_02_14_13_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemin = datex.timestamp()    
    logdate = "2024_02_14_17_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemax = datex.timestamp()    
    del_zone3 = [ttimemin, ttimemax] 
    
    logdate = "2024_02_15_14_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemin = datex.timestamp()    
    logdate = "2024_02_15_20_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemax = datex.timestamp()    
    del_zone4 = [ttimemin, ttimemax] 
    
    logdate = "2024_03_04_17_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemin = datex.timestamp()    
    logdate = "2024_03_04_18_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttimemax = datex.timestamp()    
    del_zone5 = [ttimemin, ttimemax] 
    
    logdate = "2024_03_05_13_00_00"
    datex = datetime.datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
    ttime_stop = datex.timestamp()    

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
    ts_ns = []
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
            if x[0] < ttime_start:
                continue
            elif (x[0] > del_zone1[0]) and (x[0] < del_zone1[1]):
                continue
            elif (x[0] > del_zone2[0]) and (x[0] < del_zone2[1]):
                continue
            elif (x[0] > del_zone3[0]) and (x[0] < del_zone3[1]):
                continue
            elif (x[0] > del_zone4[0]) and (x[0] < del_zone4[1]):
                continue
            elif (x[0] > del_zone5[0]) and (x[0] < del_zone5[1]):
                continue
            elif  x[0] > ttime_stop:
                break
            tstr = datetime.datetime.fromtimestamp(x[0]).strftime("%Y-%m-%d %H:%M:%S")
            ts.append(tstr)
            ts_ns.append(x[0])
            #print (type(x[0]))
            #exit()
            #ts.append(x[0])
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



    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10,6))
    plt.rcParams.update({'font.size': 14})
#    ax1 = plt.subplot(311)
#    ax2 = plt.subplot(312)
#    ax3 = plt.subplot(313)
    ax3 = plt.subplot(111)
    tsplot = pd.to_datetime(ts)


    eyms = np.array(eyms)*195
    eyss = np.array(eyss)*195
#    ax1.errorbar(ts, eums, euss, marker='o', color='C1', label="EAST APA U")
#    ax1.errorbar(ts, wums, wuss, marker='o', color='C4', label="WEST APA U")
#    ax2.errorbar(ts, evms, evss, marker='s', color='C2', label="EAST APA V")
#    ax2.errorbar(ts, wvms, wvss, marker='s', color='C5', label="WEST APA V")
    ax3.errorbar(tsplot, eyms, eyss, marker='.', color='C3', label="ENC of EAST APA Y")
    #ax3.plot(txs, tys)
#    ax3.errorbar(ts, wyms, wyss, marker='x', color='C6', label="WEST APA Y")
    #for x in range(0, int(np.max(ts))+24, 24):
    #    ax1.vlines(x, 0, 5, linestyles='dashed',color='k')
    #    ax2.vlines(x, 0, 5, linestyles='dashed',color='k')
    #    ax3.vlines(x, 0, 5, linestyles='dashed',color='k')
    ax3.set_ylim((200,1000))
    #ax2.set_ylim((0,5))
    #ax3.set_ylim((0,5))
    #ax1.set_ylabel ("RMS noise / bit")
    #ax2.set_ylabel ("RMS noise / bit")
    #ax3.set_ylabel ("RMS noise / bit")
    ax3.set_ylabel ("ENC /e$^-$")
    #ax3.set_xlabel ("Time / hour")
    #ax1.text(0,4.5,t0str)
    #ax2.text(0,4.5,t0str)
    #ax3.text(0,4.5,t0str)
    #ax1.grid(axis='y')
    #ax2.grid(axis='y')
    #ax3.grid(axis='y')
    #ax1.grid()
    #ax2.grid()
    ax3.grid()

    #ax.set_ylim([y_min, y_max])
    ax3t = ax3.twinx()
    labels = ["Temperature at Top CE Board RTD", "Temperature at Middle CE Board RTD", "Temperature at Bottom CE Board RTD"]

    for i in range(0,len(tempss)):
        txs_ns= []
        txs= []
        tys= []
        tyss= []
        for tx in temps[i]:
            if True:
                tstr = datetime.datetime.fromtimestamp(tx[0]).strftime("%Y-%m-%d %H:%M:%S")
                txs.append(tstr)
                txs_ns.append(tx[0])
                tys.append(tx[1])
                tyss.append(tx[2])
        txsplot = pd.to_datetime(txs)
        ax3t.errorbar(txsplot, tys, tyss, marker='.', color='C%d'%i, label=labels[i])
        break
    ax3t.set_ylabel("Temperature / K")
    ax3t.set_ylim([00, 350])
    #ax1.legend()
    #ax2.legend()
    ax3.legend(loc="lower right")
    ax3t.legend(loc="upper right")
    plt.gcf().autofmt_xdate(rotation=45)
    plt.title("ENC/Temperature vs. Time Distribution")
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    #plt.show()
    if rms_flg:
        plt.savefig(result_dir + "RMS_vs_Time.png")
    #else:
    #    plt.savefig(result_dir + "RMS_Cali_vs_Time.png")
    plt.close()

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10,6))
    plt.rcParams.update({'font.size': 14})

    tens = []
    for i in range(len(ts_ns)):
        for j in range(len(txs)):
            #if (tmp-txs[i]>0) and (tmp-ts[i]<1800):
            if (txs_ns[j]-ts_ns[i]>0) :
                tens.append(tys[j])
                break
    #plt.plot(tens, eyms)
    plt.errorbar(tens, eyms, eyss, marker='.', color='r', label=labels[0])
    plt.gca().invert_xaxis()
    plt.xlabel("Temperature measured at Top CE Board RTD / K")
    plt.title("ENC vs. Temperature")
    plt.ylabel("ENC /e$^-$")
    plt.grid()
    #plt.legend()
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
   # plt.show()
    plt.savefig(result_dir + "RMS_vs_Temp.png")
    plt.close()
        



#rawdir = """/Users/shanshangao/Downloads/SBND_LD/LD_result/"""
rawdir = """/scratch_local/SBND_Installation/data/commissioning/LD_result/"""
rawdir = """/Users/shanshangao/Downloads/SBND_LD/Cooldown/"""

tempss =[]
if False: # to deal with raw temperature data
#if True: # to deal with raw temperature data
    fn_map = rawdir + "./Top CE boards RTD.csv"
    temps = []
    datex = datetime.datetime.strptime("2024-02-05T00:00:00",'%Y-%m-%dT%H:%M:%S')
    t0s = datex.timestamp()
    datex = datetime.datetime.strptime("2024-03-06T00:00:00",'%Y-%m-%dT%H:%M:%S')
    t0e = datex.timestamp()
    
    avegs =[]
    ki = 0
    with open (fn_map, 'r') as fp:
        for cl in fp:
            if "\n" in cl:
                cl = cl.replace("\n", "")
            tmp = cl.split(",")
            x = []
            for i in tmp:
                x.append(i.replace(" ", ""))
            datex = datetime.datetime.strptime(x[0],'%Y-%m-%dT%H:%M:%S')
            ttmp = datex.timestamp()
    
            try:
                ttmp2 = float(x[1])
            except ValueError:
                continue
    
            if ttmp < t0s:
                continue
            elif ttmp > t0e:
                break
            else:
                if (ttmp-t0s)//1800 == ki:
                    avegs.append(ttmp2)
                else:
                    ki = (ttmp-t0s)//1800 
                    avgm = np.mean(avegs)
                    avgstd = np.std(avegs)
                    temps.append([t0s + 1800*ki - 900, avgm, avgstd])
                    avegs =[]
    
    fn_map2 = rawdir + "./Top_CE_boards_RTD.bin"
    with open (fn_map2, "wb") as fs:
        pickle.dump(temps, fs)
else:
    fn_map2 = rawdir + "./Top_CE_boards_RTD.bin"
    with open (fn_map2, "rb") as fs:
        temps = pickle.load(fs)
tempss.append(temps)


if False: # to deal with raw temperature data
#if False: # to deal with raw temperature data
    fn_map = rawdir + "./Middle East APA RTD.csv"
    temps = []
    datex = datetime.datetime.strptime("2024-02-05T00:00:00",'%Y-%m-%dT%H:%M:%S')
    t0s = datex.timestamp()
    datex = datetime.datetime.strptime("2024-03-06T00:00:00",'%Y-%m-%dT%H:%M:%S')
    t0e = datex.timestamp()
    
    avegs =[]
    ki = 0
    with open (fn_map, 'r') as fp:
        for cl in fp:
            if "\n" in cl:
                cl = cl.replace("\n", "")
            tmp = cl.split(",")
            x = []
            for i in tmp:
                x.append(i.replace(" ", ""))
            datex = datetime.datetime.strptime(x[0],'%Y-%m-%dT%H:%M:%S')
            ttmp = datex.timestamp()
    
            try:
                ttmp2 = float(x[1])
            except ValueError:
                continue
    
            if ttmp < t0s:
                continue
            elif ttmp > t0e:
                break
            else:
                if (ttmp-t0s)//1800 == ki:
                    avegs.append(ttmp2)
                else:
                    ki = (ttmp-t0s)//1800 
                    avgm = np.mean(avegs)
                    avgstd = np.std(avegs)
                    temps.append([t0s + 1800*ki - 900, avgm, avgstd])
                    avegs =[]
    
    fn_map2 = rawdir + "./Middle_East_APA_RTD.bin"
    with open (fn_map2, "wb") as fs:
        pickle.dump(temps, fs)
else:
    fn_map2 = rawdir + "./Middle_East_APA_RTD.bin"
    with open (fn_map2, "rb") as fs:
        temps = pickle.load(fs)
tempss.append(temps)

if False: # to deal with raw temperature data
#if False: # to deal with raw temperature data
    fn_map = rawdir + "./Bottom East RTD.csv"
    temps = []
    datex = datetime.datetime.strptime("2024-02-05T00:00:00",'%Y-%m-%dT%H:%M:%S')
    t0s = datex.timestamp()
    datex = datetime.datetime.strptime("2024-03-06T00:00:00",'%Y-%m-%dT%H:%M:%S')
    t0e = datex.timestamp()
    
    avegs =[]
    ki = 0
    with open (fn_map, 'r') as fp:
        for cl in fp:
            if "\n" in cl:
                cl = cl.replace("\n", "")
            tmp = cl.split(",")
            x = []
            for i in tmp:
                x.append(i.replace(" ", ""))
            datex = datetime.datetime.strptime(x[0],'%Y-%m-%dT%H:%M:%S')
            ttmp = datex.timestamp()
    
            try:
                ttmp2 = float(x[1])
            except ValueError:
                continue
    
            if ttmp < t0s:
                continue
            elif ttmp > t0e:
                break
            else:
                if (ttmp-t0s)//1800 == ki:
                    avegs.append(ttmp2)
                else:
                    ki = (ttmp-t0s)//1800 
                    avgm = np.mean(avegs)
                    avgstd = np.std(avegs)
                    temps.append([t0s + 1800*ki - 900, avgm, avgstd])
                    avegs =[]
    
    fn_map2 = rawdir + "./Bottom_East_RTD.bin"
    with open (fn_map2, "wb") as fs:
        pickle.dump(temps, fs)
else:
    fn_map2 = rawdir + "./Bottom_East_RTD.bin"
    with open (fn_map2, "rb") as fs:
        temps = pickle.load(fs)
tempss.append(temps)

#exit()
#txs= []
#tys= []
#for tx in temps:
#    if tx[0] < ttime_start:
#        continue
#    elif tx[0] > ttime_stop:
#        break
#    else:
#        tstr = datetime.datetime.fromtimestamp(tx[0]).strftime("%Y-%m-%d %H:%M:%S")
#        txs.append(tstr)
#        tys.append(tx[1])


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
TempRMS_TS_ANA(copy.deepcopy(rmsts), result_dir, tempss, rms_flg=True)
#TempRMS_TS_ANA(copy.deepcopy(rmsts), result_dir, rms_flg=False)


