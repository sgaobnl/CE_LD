# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/23/2025 2:14:21 PM
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
import pytz
import struct
import codecs
import pickle
from shutil import copyfile
import shutil
import numpy as np
import h5py
from scipy.signal import find_peaks
from zoneinfo import ZoneInfo


fm = """D:/GitHub/CE_LD/chn_mapping.csv""" #femb1
fm = """C:/uFEMB/CE_LD/chn_mapping.csv""" #femb2
fm = """C:/Users/sgao.BNL/Documents/GitHub/CE_LD/chn_mapping.csv"""

dmap = {}
if os.path.isfile(fm):    
    with open(fm,"r") as f:
        for line in f:
            if "femb" in line:
                continue
            else:
                tmps = line.split(",")
                chno=int(tmps[6])
                if len(tmps[12]) >= 0:
                    sipmno=tmps[12][0:3] +"_"+ tmps[9] +"_"+tmps[11] +"_" + "CH%02d"%chno + "_FNL" + tmps[4] 
                    dmap[chno] = sipmno
else:
    print ("%s doesn't exist"%fm)
    exit()    


def create_grp_hdf5(hdf5_fp):
    if os.path.exists(hdf5_fp):
        print("File exists.")   
    else:
        with h5py.File(hdf5_fp, 'w') as f:
            maxshape = (None,)
            #for chi in range(32):
            for onekey in dmap.keys():
                sipmno = dmap[onekey]
                if 'OPEN' not in sipmno:
                    grp = f.create_group(sipmno)
        print("File and groups created.")


rootdir = """H:/SiPM/"""
create_grp_hdf5(hdf5_fp = rootdir + "led_cali_vs_time.hdf5")


def append_data(hdf5_fp, sipmno, dsetn, dsetd, attrsd):
    with h5py.File(hdf5_fp, 'a') as f:
        subgrp=f['/'+sipmno]
        ds = subgrp.get(dsetn, default=None)
        if ds is None:
            subgrp.create_dataset(dsetn, data=dsetd,  dtype=np.dtype([("PeakADC","u2"), ("PeakCNT", "u2")]))
            for onekey in attrsd.keys():
                ds=subgrp[dsetn]
                ds.attrs[onekey] = attrsd[onekey] 
        else:
            pass


subdirs = [ 
            "Rawdata_20250505_15_57/",
            "Rawdata_20250505_17_45/",
            "Rawdata_20250506_00_00/",
            "Rawdata_20250507_00_00/",
            "Rawdata_20250508_00_00/",
            "Rawdata_20250509_00_00/",
            "Rawdata_20250509_12_35/",
            "Rawdata_20250509_12_38/",
            "Rawdata_20250509_14_28/",
            "Rawdata_20250509_14_34/",
            "Rawdata_20250509_14_38/",
            "Rawdata_20250510_00_00/",
            "Rawdata_20250511_00_00/",
            "Rawdata_20250512_00_00/",
            "Rawdata_20250513_00_00/",
            "Rawdata_20250514_00_00/",
            "Rawdata_20250515_00_00/",
            "Rawdata_20250516_00_00/",
            "Rawdata_20250517_00_00/",
            "Rawdata_20250518_00_00/",
            "Rawdata_20250519_00_00/",
            "Rawdata_20250520_00_00/",
            "Rawdata_20250521_00_00/",
            "Rawdata_20250522_00_00/",
            ]

for subdir in subdirs:
    print (subdir)
    date_str=subdir[8:-1]
    
    raw_dir = rootdir + subdir
    ana_dir = rootdir + "Ana" + subdir[4:]
    rst_dir = rootdir + "Result" + subdir[7:]
    bak_dir = rootdir + "Bak" + subdir[4:]
    
    if not os.path.exists(rst_dir):
        print ("folder does not exist")
        exit()
    
    
    for ufemb_id in [1,2]:
        hdf5_fp=rst_dir + "ufemb%d_%s_trigger.hdf5"%(ufemb_id, subdir[8:16])
        if os.path.isfile(hdf5_fp):    
            print (hdf5_fp)
            pass
        else:
            continue
    
        with h5py.File(hdf5_fp, "r") as f:

            fns = f["file_analyzed"][:]
            fns.sort()
            fn0 = fns[0]
            fn0 = fn0.decode('utf-8')
            postana = fn0.find(".tana")
            ts0 = int(fn0[postana-32:postana])
            dt0 = datetime.strptime(fn0[7:7+14], "%Y%m%d_%H_%M").replace(tzinfo=ZoneInfo("America/New_York") )#timezone.utc)
            dtt0 = int(dt0.timestamp())

            #for ch in [49-32]:
            for ch in range(32):
                key = "CH%02d"%ch
                bypass_ch_flg = False
                dn = dmap[(ufemb_id-1)*32+ch]
                if "OPEN" in dn:
                    print (dn, "is ignored")
                    continue
                plt_dir = rst_dir + dn  + "_plots/Triggers/"
                if not os.path.exists(plt_dir):
                    try:
                        os.makedirs(plt_dir)
                    except OSError:
                        print ("Error to create folder %s"%plt_dir)
                        sys.exit()
        
                data = f[key]
                data=data[:]
                if len(data) > 0:
                    ts,ds = zip(*data)
                    ts = np.array(ts)-ts0*10
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
                            prev=idx+1
                            continue
                        posb = poss[0]
                        pose = poss[-1]
                        subt = subt[posb:pose]
                        subd = subd[posb:pose]
        
                        subts.append(subt)
                        subds.append(subd)
                        prev = idx + 1
                    subts.append(ts[prev : ].copy())
                    subds.append(ds[prev : ].copy())
        
                    for xi in range(len(subts)):
        
                        dtt00 = dtt0 + int(subts[xi][0]//1e9) 
                        easten=pytz.timezone("America/New_York")
                        dt = datetime.fromtimestamp(dtt00, tz=easten)
        
        
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

                        import matplotlib.pyplot as plt
                        # Create a 2x2 grid of subplots
                        fig, axes = plt.subplots(2, 1, figsize=(8, 10))
        
                        fig.suptitle(dn + " with data starting at {}".format(dt.strftime("%Y-%m-%d %H:%M:%S")))
        
                         # Top-left plot
                        axes[0].scatter((np.array(subts[xi])- subts[xi][0])/1e9 , subds[xi], color='green', marker='.')
                        axes[0].set_title('SiPM Output')
                        axes[0].set_xlabel('Time / s')
                        axes[0].set_ylabel('Amplitude Peak / ADC bit')
                        axes[0].set_ylim((0,2000))
                        axes[0].grid()
       
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
        
                        fig.savefig(pltfp, format='png')                 
                        #plt.show()
                        plt.close()

                        #write to hdf5 results#################
                        attrsd = {}
                        attrsd["Start_TS"] = subts[xi][0] + ts0
                        attrsd["End_TS"] = subts[xi][-1] + ts0
                        attrsd["Total Triggers"] = len(subds[xi])
                        if (np.max(peak_heights) > len(subds[xi]) *0.8) or (len(peak_heights) < 3) or (np.max(peak_centers) < 20):
                            attrsd["Trigger Type"] = "Charge" 
                        else:
                            attrsd["Trigger Type"] = "LED" 
                        attrsd["Plot_url"] = pltfp
                        dsetd = list(zip(peak_centers, peak_heights))
                        append_data(hdf5_fp=rootdir + "led_cali_vs_time.hdf5", sipmno=dn, dsetn=dt.strftime("%Y_%m_%d_%H_%M_%S"), dsetd=dsetd, attrsd=attrsd)


