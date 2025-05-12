# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/8/2025 4:40:59 PM
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
from datetime import datetime, timezone
import struct
import codecs
import pickle
from shutil import copyfile
import shutil
import numpy as np
import h5py
from scipy.signal import find_peaks



rootdir = """D:/tmppp/sipm/"""
subdir = "Rawdata_20250502_15_46/"
date_str=subdir[8:-1]
dt = datetime.strptime(date_str, "%Y%m%d_%H_%M").replace(tzinfo=timezone.utc)
dtt0 = int(dt.timestamp())

#ufemb_id = int(input ("Choose a uFEMB(1-2):"))
ufemb_id = 2
if ufemb_id not in [1,2]:
    exit()
#chin = int(input ("Choose a CH(0-31):"))

#if chin>=32:
#    exit()
#hi0 = int(input ("Hours after %s: "%subdir[8:-1]))
hi0 = 0


raw_dir = rootdir + subdir
ana_dir = rootdir + "Ana" + subdir[4:]
rst_dir = rootdir + "Result" + subdir[7:]
bak_dir = rootdir + "Bak" + subdir[4:]

if not os.path.exists(rst_dir):
    print ("folder does not exist")
    exit()

hdf5_fp=rst_dir + "ufemb%d_darkrate.hdf5"%ufemb_id
hdf5_fp=rst_dir + "ufemb%d_trigger.hdf5"%ufemb_id
#hdf5_fp=rst_dir + "trigger.hdf5"

with h5py.File(hdf5_fp, "r") as f:
    #for ch in [chin]:
    for ch in range(32):
        key = "CH%02d"%ch
        bypass_ch_flg = False
        plt_dir = rst_dir + "CH%d"%((ufemb_id-1)*32+ch)  + "_plots/Triggers/"
        if not os.path.exists(plt_dir):
            try:
                os.makedirs(plt_dir)
            except OSError:
                print ("Error to create folder %s"%plt_dir)
                sys.exit()

        data = f[key]
        data=data[:]
        h2s = 3600
        if len(data) > 0:
            ts,ds = zip(*data)
            ts = np.array(ts)
            ds = np.array(ds)
            diffs = ts[1:] - ts[:-1]

            jumps = np.where(diffs > 1e9)[0]
            subts = []
            subds = []
            prev = 0
            for idx in jumps:
                subt = ts[prev : idx + 1].copy()
                subd = ds[prev : idx + 1].copy()
                poss = np.where(subd > 30)[0]
                if len(poss) < 10:
                    bypass_ch_flg = True
                    break
                posb = poss[0]
                pose = poss[-1]
                subt = subt[posb:pose]
                subd = subd[posb:pose]

                subts.append(subt)
                subds.append(subd)
                prev = idx + 1
            if bypass_ch_flg:
                continue
            subts.append(ts[prev : ].copy())
            subds.append(ds[prev : ].copy())

            for xi in range(len(subts)):

                dtt00 = dtt0 + int(subts[xi][0]//1e9)
                dt = datetime.fromtimestamp(dtt00)

                import matplotlib.pyplot as plt
                # Create a 2x2 grid of subplots
                fig, axes = plt.subplots(2, 1, figsize=(8, 10))

                fig.suptitle("Start Time {}".format(dt.strftime("%Y-%m-%d %H:%M:%S")))

                 # Top-left plot
                axes[0].scatter((np.array(subts[xi])- subts[xi][0])/1e9 , subds[xi], color='green', marker='.')
                axes[0].set_title('SiPM Output')
                axes[0].set_xlabel('Time / s')
                axes[0].set_ylabel('Amplitude Peak / ADC bit')
                axes[0].set_ylim((0,2000))
                axes[0].grid()

                vbinw=10
                # 1) Build histogram
                counts, bin_edges = np.histogram(subds[xi], bins=range(min(subds[xi]), max(subds[xi])+vbinw, vbinw))
                # 2) Find local maxima in the counts
                #    You can tweak `prominence` or `distance` to suit your data.
                peaks, properties = find_peaks(counts, prominence=20, distance=3)
                
                # 3) Compute bin centers for each peak
                bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
                peak_centers = bin_centers[peaks]
                peak_heights = counts[peaks]


                axes[1].hist(subds[xi], bins=range(min(subds[xi]), max(subds[xi])+vbinw, vbinw), color='blue', edgecolor='black')

                for x, h in zip(peak_centers, peak_heights):
                    axes[1].axvline(x, color='red', linestyle='--')
                    x = int(x)
                    axes[1].annotate(f'{x:d}', 
                                xy=(x, h), 
                                xytext=(0, 8), 
                                textcoords='offset points',
                                ha='center', color='red')

                axes[1].set_title('Amplitude distribution')
                axes[1].set_xlabel('Amplitude / ADC bit')
                axes[1].set_ylabel('Counts')
                axes[1].set_yscale('log')
                axes[1].grid()
  
                
                plt.tight_layout()
    
                pltfp = plt_dir + "ufemb%d_CH%d_Trig_%s.png"%(ufemb_id,ch,dt.strftime("%Y_%m_%d_%H_%M_%S"))
                print (pltfp)

                fig.savefig(pltfp, format='png')                 
                #plt.show()
                #plt.close()


#            import matplotlib.pyplot as plt
#            #plt.plot(ts,ds)
#            #@plt.plot(subts[0],subds[0])
#            plt.hist(subds[0], bins=range(min(subds[0]), max(subds[0])+10, 10), color='purple')
#            plt.yscale('log')
#            plt.show()
#            plt.close()


            if False:
                if hi0 == 0:
                    ts_start = 0
                    ts_end = 1e9 
                else:
                    ts_start = hi0*1e9*3600
                    ts_end = (hi0+1)*1e9*3600
    
    
                if ts_start > ts[-1]:
                    print ("data hasn't taken that long")
                    exit()
    
                if ts[-1] < ts_end:
                    ts_end=ts[-1]
    
                ts=np.array(ts)
                subts= ts[(ts>ts_start)&(ts<ts_end)]
                if len(subts) <= 0:
                    print ("no data during this period")
                    exit()
                subts_pos0 = np.where(ts == subts[0])[0][0]
                subds = ds[subts_pos0: subts_pos0 + len(subts)]
    
                cutoffhz=20
                vbinw=10
    
                subts2=np.array(subts)-subts[0]
                f1hz_1s = []
                i=0
                dlt=1
                for i in range(h2s):
                    ti = subts2[(subts2>i*dlt*1e9)&(subts2<=(i+1)*dlt*1e9)]
                    f1hz_1s.append(len(ti))
                    i = i + 1
                f1hz_1s2 = np.array(f1hz_1s)  
                f1hz_1s2 = f1hz_1s2[f1hz_1s2 < cutoffhz]  
    
                avghz =  (len(subts)/3600)
                avghz2= (f1hz_1s2.sum()/len(f1hz_1s2))
    
    
                if True:
                    import matplotlib.pyplot as plt
    
                    # Create a 2x2 grid of subplots
                    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
                    fig.suptitle("Hour#%d"%hi0)
    
                    # Top-left plot
                    axes[0, 0].scatter(np.arange(h2s), f1hz_1s, color='red', marker='.')
                    axes[0, 0].set_title('Dark Rate')
                    axes[0, 0].set_xlabel('Time / s')
                    axes[0, 0].set_ylabel('Dark Rate / Hz')
                    axes[0, 0].set_yscale('log')
                    axes[0, 0].grid()
                    
                    # Top-right plot
                    axes[0, 1].scatter(np.array(subts2)/1e9, subds, color='green', marker='.')
                    axes[0, 1].set_title('SiPM Output')
                    axes[0, 1].set_xlabel('Time / s')
                    axes[0, 1].set_ylabel('Amplitude Peak / ADC bit')
                    axes[0, 1].set_ylim((0,2000))
                    axes[0, 1].grid()
                    
                    # Bottom-left plot
                    axes[1, 0].hist(f1hz_1s, bins=range(min(f1hz_1s), max(f1hz_1s)+1, 1), color='blue', label="Avg = %.02f Hz"%avghz)
                    axes[1, 0].hist(f1hz_1s2, bins=range(min(f1hz_1s2), max(f1hz_1s2)+1, 1), color='m', label="Avg(<20Hz) = %.02f Hz"%avghz2)
                    axes[1, 0].set_title('Dark Rate Frequency distribution')
                    axes[1, 0].set_xlabel('Dark Rate / Hz')
                    axes[1, 0].set_ylabel("Counts")
                    axes[1, 0].set_yscale('log')
                    axes[1, 0].legend()
                    axes[1, 0].grid()
                    
                    # Bottom-right plot
                    axes[1, 1].hist(subds, bins=range(min(subds), max(subds)+vbinw, vbinw), color='purple')
                    axes[1, 1].set_title('Dark Rate Amplitude distribution')
                    axes[1, 1].set_xlabel('Amplitude / ADC bit')
                    axes[1, 1].set_ylabel('Counts')
                    axes[1, 1].set_yscale('log')
                    axes[1, 1].grid()
                    
                    plt.tight_layout()
    
                   
                    plt.show()
                    plt.close()

