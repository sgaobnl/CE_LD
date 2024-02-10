# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Fri Feb  9 23:36:47 2024
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
from fft_chn import chn_rfft_psd

result_dir = "./LD_result/"


def FEMB_CHK(fembdata, rms_f = False, fs="./"):
    RAW_C = RAW_CONV()
    chn_rmss = []
    chn_rmss_filtered = []
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
            maxloc = np.where(achn_ped == np.max(achn_ped))[0][0]
            if maxloc < 50:
                achn_ped_sub = achn_ped[50:]
            elif maxloc > len(achn_ped)-50:
                achn_ped_sub = achn_ped[0:-50]
            else:
                achn_ped_sub = achn_ped[0:maxloc-50] + achn_ped[maxloc+50:] 
            minloc = np.where(achn_ped == np.min(achn_ped))[0][0]
            if minloc < 50:
                achn_ped_sub2 = achn_ped_sub[50:]
            elif minloc > len(achn_ped_sub)-50:
                achn_ped_sub2 = achn_ped_sub[0:-50]
            else:
                achn_ped_sub2 = achn_ped_sub[0:maxloc-50] + achn_ped_sub[maxloc+50:] 

            arms = np.std(achn_ped)
            arms_2 = np.std(achn_ped_sub2)
            aped = int(np.mean(achn_ped))
            apeakp = int(np.mean(chn_peakp[achn]))
            apeakn = int(np.mean(chn_peakn[achn]))
            chn_rmss.append(arms)
            chn_rmss_filtered.append(arms_2)
            chn_peds.append(aped)
            chn_pkps.append(apeakp)
            chn_pkns.append(apeakn)
            #chn_waves.append( chn_data[achn][feed_loc[0]: feed_loc[1]] )
            #chn_waves.append( chn_data[achn] )
            #avg_cnt = len(feed_loc)-2

            #avg_wave = np.array(chn_data[achn][feed_loc[0]: feed_loc[0] + 100]) 
            #for i in range(1, avg_cnt,1):
            #    #avg_wave += np.array(chn_data[achn][feed_loc[i]: feed_loc[i+1]]) 
            #    avg_wave += np.array(chn_data[achn][feed_loc[i]: feed_loc[i]+100]) 
            #avg_wave = avg_wave/avg_cnt
            #chn_avg_waves.append(avg_wave)
    ana_err_code = ""
    rms_mean = np.mean(chn_rmss)

    for gi in range(8): 
        ped_mean = np.mean(chn_peds[gi*16 : (gi+1)*16])
        pkp_mean = np.mean(chn_pkps[gi*16 : (gi+1)*16])
        pkn_mean = np.mean(chn_pkns[gi*16 : (gi+1)*16])
        ped_thr= 30 

    result = (True, "pass-", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_rmss_filtered])
#    FEMB_PLOT(result, fn=fs.replace(".bin", ".png"))
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

def SBND_ANA(rawdir, rms_f=False, rn="./result.ln"):
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
        chn_rmss_filtered = results[2][4]
        #chn_wfs =  results[2][4]
        #chn_avgwfs =  results[2][5]
    
        for i in range(lendec):
            if (int(dec_chn[i][5]) == crateno) and (int(dec_chn[i][6]) == wibno ) and (int(dec_chn[i][7]) == fembno ) :
                decch = int(dec_chn[i][8])
                dec_chn[i].append(chn_rmss[decch])
                dec_chn[i].append(chn_peds[decch])
                dec_chn[i].append(chn_pkps[decch])
                dec_chn[i].append(chn_pkns[decch])
                dec_chn[i].append(chn_rmss_filtered[decch])
                #dec_chn[i].append((chn_wfs[decch]))
                #dec_chn[i].append((chn_avgwfs[decch]))
         
#    fr = result_dir + "/" + rn + ".ld" 
    with open(rn, 'wb') as f:
        pickle.dump(dec_chn, f)
    #fr =rawdir + "test_results"+".csv" 
    #with open (fr, 'w') as fp:
    #    top_row = "APA,Crate,FEMB_SN,POSITION,WIB_CONNECTION,Crate_No,WIB_no,WIB_FEMB_LOC,FEMB_CH,Wire_type,Wire_No,,RMS Noise, Pedestal, Pulse_Pos_Peak, Pulse_Neg_Peak, RMS(filtered),"
    #    fp.write( top_row + "\n")
    #    for x in dec_chn:
    #        fp.write(",".join(str(i) for i in x[0:17]) +  "," + "\n")
    #return dec_chn

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
    
def DIS_PLOT(dec_chn, fdir, title = "RMS Noise Distribution", fn = "SBND_APA_RMS_DIS.png", ns=[1], ylim=[-2,10], ylabel = "RMS / bit"):
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
        ax1.plot(chns, vals, color="C%d"%(n+1), marker='.', mfc='b', mec='b', label = "U" )
        chns, vals=list(zip(*sorted(wuvals, key=operator.itemgetter(0))))
        ax2.plot(chns, vals, color="C%d"%(n+1), marker='.', mfc='b', mec='b', label = "U" )

        chns, vals=list(zip(*sorted(evvals, key=operator.itemgetter(0))))
        ax1.plot(np.array(chns)+1984, vals, color="C%d"%(n+1), marker='.', mfc='g', mec='g',  label = "V" )
        chns, vals=list(zip(*sorted(wvvals, key=operator.itemgetter(0))))
        ax2.plot(np.array(chns)+1984, vals, color="C%d"%(n+1), marker='.', mfc='g', mec='g',  label = "V" )

        chns, vals=list(zip(*sorted(eyvals, key=operator.itemgetter(0))))
        ax1.plot(np.array(chns)+1984*2, vals, color="C%d"%(n+1), marker='.', mfc='r', mec='r',  label = "Y" )
        chns, vals=list(zip(*sorted(wyvals, key=operator.itemgetter(0))))
        ax2.plot(np.array(chns)+1984*2, vals, color="C%d"%(n+1), marker='.', mfc='r', mec='r',  label = "Y" )
    ax1.set_ylim((ylim))
    ax1.set_xlim((0,6000))
    ax1.set_ylabel (ylabel)
    ax1.set_xlabel ("Channel NO.")
    ax1.set_title ("EAST APA: " + title)
#    ax1.legend()
    ax1.grid()

    ax2.set_ylim((ylim))
    ax2.set_xlim((0,6000))
    ax2.set_ylabel (ylabel)
    ax2.set_xlabel ("Channel NO.")
    ax2.set_title ("WEST APA: " + title)
#    ax2.legend()
    ax2.grid()


    ffig = fdir + fn
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    #plt.savefig(ffig)
    print ("result saves at {}".format(ffig))
    plt.show()
    plt.close()


def DIS_CHN_PLOT(dec_chn, chnstr="U1"):
    apa = chnstr[0]
    wiretype = chnstr[1]
    wireno = int(chnstr[2:])
    for d in dec_chn:
        if (apa in d[0]) and (wiretype in d[9]) and (wireno == int(d[10])) and (len(d) >12):
            APA = d[0]
            Crate = d[1]
            FEMB_SN = d[2]
            POSITION = d[3]
            WIB_CONNECTION = d[4]
            Crate_No = d[5]
            WIB_no = d[6]
            WIB_FEMB_LOC = d[7]
            FEMB_CH = d[8]
            Wire_type = d[9]
            Wire_No = d[10]
            RMS = d[12]
            Pedmean = d[13]
            Plspp = d[14]
            Plsnp = d[15]
            wfs = d[16]
            avgwfs = d[17]
        #else:
        #    print ("Channel without valid data...")
            import matplotlib.pyplot as plt

            fig = plt.figure(figsize=(8.5,8))
            fig.suptitle("Test Result of %s"%chnstr, weight ="bold", fontsize = 12)
            fig.text(0.10, 0.94-0.02, "APA: {}".format(APA)   )
            fig.text(0.55, 0.94-0.02, "Crate: {}".format(Crate)   )
            fig.text(0.10, 0.90-0.02, "FEMB SN: {}".format(FEMB_SN)   )
            fig.text(0.55, 0.90-0.02, "WIB CONNECTION: {}".format(WIB_CONNECTION)   )
            fig.text(0.10, 0.86-0.02, "Crate No: {}".format(Crate_No)   )
            fig.text(0.55, 0.86-0.02, "WIB No: {}".format(WIB_no)   )
            fig.text(0.10, 0.82-0.02, "WIB FEMB SLOT: {}".format(WIB_FEMB_LOC)   )
            fig.text(0.55, 0.82-0.02, "CHN on FEMB: {}".format(FEMB_CH)   )
            fig.text(0.10, 0.78-0.02, "Wire Type: {}".format(Wire_type)   )
            fig.text(0.55, 0.78-0.02, "Wire No.: {}".format(Wire_No)   )

            fig.text(0.10, 0.72-0.02, "RMS noise / bit: {:0.3f}".format(RMS), weight ="bold", color = 'b'  )
            fig.text(0.55, 0.72-0.02, "Pedestal / bit: {}".format(Pedmean) , weight ="bold", color = 'b'  )
            fig.text(0.10, 0.68-0.02, "Maximum Amplitude / bit: {}".format(Plspp) , weight ="bold", color = 'b'  )
            fig.text(0.55, 0.68-0.02, "Minmum Amplitude / bit: {}".format(Plsnp) , weight ="bold", color = 'b'  )

            ax1 = plt.subplot2grid((3, 2), (1, 0), colspan=1, rowspan=1)
            ax2 = plt.subplot2grid((3, 2), (2, 0), colspan=1, rowspan=1)
            ax3 = plt.subplot2grid((3, 2), (1, 1), colspan=1, rowspan=1)
            ax4 = plt.subplot2grid((3, 2), (2, 1), colspan=1, rowspan=1)

            if len(wfs) > 500:
                wlen = 500
            else:
                wlen = len(wfs)
            x = np.arange(wlen)
            y = wfs[0:wlen]
            FEMB_SUB_PLOT(ax1, x, y, title="Waveform", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C0')

            wlen = len(wfs)
            x = np.arange(wlen)
            y = wfs[0:wlen]
            FEMB_SUB_PLOT(ax2, x, y, title="Waveform", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C1')

            wlen = len(avgwfs)
            x = np.arange(wlen)
            y = avgwfs[0:wlen]
            FEMB_SUB_PLOT(ax3, x, y, title="Averaging Waveform", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C2')

            f,p = chn_rfft_psd(wfs,  fft_s = len(wfs), avg_cycle = 1)
            FEMB_SUB_PLOT(ax4, f, p, title="FFT ", xlabel="Frequency / Hz", ylabel=" / dB", color='C3')
            
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.show()
            #print ("result saves at {}".format(ffig))
            #plt.savefig(fn)
            plt.close()



rawdir = """/Users/shanshangao/Downloads/SBND_LD/2024_02_06/LD_2024_02_06_00_00_05/"""
rawdir = """/Users/shanshangao/Downloads/SBND_LD/2024_02_06/LD_2024_02_06_12_26_03/"""
rawdir = """/Users/shanshangao/Downloads/SBND_LD/2024_02_06/LD_2024_02_06_13_24_29/"""
rawdir = """/Users/shanshangao/Downloads/SBND_LD/2024_02_07/LD_2024_02_07_00_13_55/"""
rawdir = """/Users/shanshangao/Downloads/SBND_LD/2024_02_07/LD_2024_02_07_13_06_36/"""
rawdir = """/Users/shanshangao/Downloads/SBND_LD/2024_02_09/LD_2024_02_09_08_01_51/"""
rawdir = """/Users/shanshangao/Downloads/SBND_LD/2024_02_09/LD_2024_02_09_20_19_55/"""
rawdir = """/Users/shanshangao/Downloads/SBND_LD/"""
#fr =rawdir + "test_results"+".result" 
#if (os.path.isfile(fr)):
#    with open(fr, 'rb') as f:
#        result = pickle.load(f)
#    pass
#else:
#    #if "RMS" in rawdir:
#    #    rms_f = True
#    #else:
result_dir = "./LD_result/"
d1ns = []
for root, dirs, files in os.walk(rawdir):
    for d1n in dirs:
        if ("2024_" in d1n) :
            d1ns.append(rawdir + d1n + "/")
    break

for d1n in d1ns:
    for root, dirs, files in os.walk(d1n):
        for d2n in dirs:
            if ("LD_2024_" in d2n) :
                anadir = d1n + d2n + "/"
                print (anadir)
                rn = result_dir + "/" + d2n + ".ld"
                if (os.path.isfile(rn)):
                    pass
                else:
                    rms_f = False
                    result = SBND_ANA(anadir, rms_f = rms_f, rn=rn)
        exit()
        break


#DIS_PLOT(dec_chn=result, fdir=rawdir, title = "RMS Noise Distribution", fn = "SBND_APA_RMS_DIS.png", ns=[1], ylim=[-2,8])
#DIS_PLOT(dec_chn=result, fdir=rawdir, title = "Pulse Response Distribution", fn = "SBND_APA_PLS_DIS.png", ns=[2,3,4], ylim=[-100,4000], ylabel="Amplitude / bit")
#
#while True:
#    print ("Input a chnanel number following format (E/W)(U/V/Y)(Chn no.), e.g. EU0001")
#    xstr = input ("Input a channel number  > ")
#    if (len(xstr)>2) and (("E" in xstr[0]) or ("W" in xstr[0])) and (("U" in xstr[1]) or ("V" in xstr[1]) or ("Y" in xstr[1])):
#        try:
#            wno = int(xstr[2:])
#            DIS_CHN_PLOT(dec_chn=result, chnstr=xstr)
#        except ValueError:
#            print ("Wrong number, please input again")
#    else:
#        yns = input ("Exit Y/N")
#        if ("Y" in yns) or ("y" in yns):
#            exit()
#
    



    

