# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 6/11/2025 10:20:36 AM
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
import pickle
from shutil import copyfile
import shutil
import numpy as np
import h5py
from scipy.signal import find_peaks
from zoneinfo import ZoneInfo
import pytz


def create_grp_hdf5(hdf5_fp):
    if os.path.exists(hdf5_fp):
        pass
    else:
        with h5py.File(hdf5_fp, 'w') as f:
            maxshape = (None,)
            #for chi in range(32):
            for onekey in dmap.keys():
                sipmno = dmap[onekey]
                if 'OPEN' not in sipmno:
                    grp = f.create_group(sipmno)
            dt = h5py.string_dtype(encoding='utf-8')
            f.create_dataset("file_analyzed", shape=(0,), maxshape=maxshape, dtype=dt, chunks=True)

        print("File and groups created.")

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
            for onekey in attrsd.keys():
                ds=subgrp[dsetn]
                ds.attrs[onekey] = attrsd[onekey] 

def append_anaed_fp( hdf5_fp, anafp):
    with h5py.File(hdf5_fp, 'a') as f:
        dset=f["file_analyzed"]
        old_size = dset.shape[0]
        new_size = old_size+1
        dset.resize((old_size + 1,))
        dset[old_size:] = anafp

def filter_anaed_file( hdf5_fp, anafp  ):
    with h5py.File(hdf5_fp, 'r') as f:
        dset=f["file_analyzed"]
        fns = dset[:]
        dt0 = datetime.now()
        dtt0 = int(dt0.timestamp()) - 3600*20
        easten=pytz.timezone("America/New_York")
        dt = datetime.fromtimestamp(dtt0, tz=easten)
        print (dt.strftime("%Y%m%d"))

        for fn in fns:
            #if (anafp in str(fn)) and (datetime.now().strftime("%Y%m%d") not in str(fn)) and ("20250530" not in str(fn))and ("20250531" not in str(fn))and ("20250601" not in str(fn)):
            if (anafp in str(fn)) and (datetime.now().strftime("%Y%m%d") not in str(fn)) and (dt.strftime("%Y%m%d") not in str(fn)):
                return True
        return False

def hdf5_dr_plot_step3():
    fm = """D:/GitHub/CE_LD/chn_mapping.csv""" #femb1
    #fm = """C:/uFEMB/CE_LD/chn_mapping.csv""" #femb2
    #fm = """C:/Users/sgao.BNL/Documents/GitHub/CE_LD/chn_mapping.csv"""
    
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
    
    
    rootdir = """G:/SiPM/"""
    drfp = rootdir + "darkrate_vs_time.hdf5"
    create_grp_hdf5(hdf5_fp = drfp)
    
    #subdirs = [#"Rawdata_20250505_15_57/",
    #           # "Rawdata_20250505_17_45/",
    #           # "Rawdata_20250506_00_00/",
    #           # "Rawdata_20250507_00_00/",
    #           # "Rawdata_20250508_00_00/",
    #           # "Rawdata_20250509_00_00/",
    #           # "Rawdata_20250509_12_35/",
    #           # "Rawdata_20250509_12_38/",
    #           # "Rawdata_20250509_14_28/",
    #           # "Rawdata_20250509_14_34/",
    #           # "Rawdata_20250509_14_38/",
    ##            "Rawdata_20250510_00_00/",
    ##            "Rawdata_20250511_00_00/",
    ##            "Rawdata_20250512_00_00/",
    ##            "Rawdata_20250513_00_00/",
    ##            "Rawdata_20250514_00_00/",
    ##            "Rawdata_20250515_00_00/",
    ##            "Rawdata_20250516_00_00/",
    ##            "Rawdata_20250517_00_00/",
    #            "Rawdata_20250518_00_00/",
    ##            "Rawdata_20250519_00_00/",
    #            ]
    
    for root, dirs, files in os.walk(rootdir):
        break
    
    rstdirs = []
    for onedir in dirs:
        #if ("Result_" in onedir) and (datetime.now().strftime("%Y%m%d") not in onedir):
        if ("Result_" in onedir) :
        #if ("Result_" in onedir) and (datetime.now().strftime("%Y%m%d") in onedir):
            rstdirs.append(onedir)
    
    
    for subdir in rstdirs:
        rst_dir = rootdir + subdir + "/"
        
        if not os.path.exists(rst_dir):
            print ("folder does not exist")
            exit()
        
        for ufemb_id in [1,2]:
            hdf5_fp=rst_dir + "ufemb%d_%s_darkrate.hdf5"%(ufemb_id, subdir[7:15])
            if os.path.isfile(hdf5_fp):    
                print (hdf5_fp)
                pass
            else:
                continue
    
            if filter_anaed_file(hdf5_fp=drfp, anafp=hdf5_fp  ):
                print (hdf5_fp, "was analyzed")
                continue    
            with h5py.File(hdf5_fp, "r") as f:
    
                fns = f["file_analyzed"][:]
                fns.sort()
                fn0 = fns[0]
                fn0 = fn0.decode('utf-8')
                postana = fn0.find(".ana")
                ts0 = int(fn0[postana-32:postana])
                dt0 = datetime.strptime(fn0[7:7+14], "%Y%m%d_%H_%M").replace(tzinfo=ZoneInfo("America/New_York") )#timezone.utc)
                dtt0 = int(dt0.timestamp())
    
                for ch in range(32):
                    key = "CH%02d"%ch
                    dn = dmap[(ufemb_id-1)*32+ch]
                    if "OPEN" in dn:
                        print (dn, "is ignored")
                        continue
                    print (dn, "is being analyzed")
    
                    plt_dir = rst_dir + dn  + "_plots/DarkRate/"
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
                        ts = np.array(ts) - ts0*10
                        tlen = int(ts[-1])
                        cutoffhz=20
                        vbinw=10
    
                        for hi in range (int(tlen//(1e9*h2s)) + 1):
                            subts = ts[(ts>hi*h2s*1e9)&(ts<=(hi+1)*h2s*1e9)]
                            dtt00 = dtt0 + hi*3600
                            easten=pytz.timezone("America/New_York")
                            dt = datetime.fromtimestamp(dtt00, tz=easten)

                            pltfp = plt_dir + "DarkRate_%s_%s.png"%(dn, dt.strftime("%Y_%m_%d_%H"))
                            
                            current_hr_flg = ( dt.strftime("%Y_%m_%d_%H") == datetime.now().strftime("%Y_%m_%d_%H") ) 
                            if (os.path.exists(pltfp)) and  (not current_hr_flg):
                                continue
                            else:
                                print ( pltfp, " is generating")

    
                            if len(subts) <= 0:
                                print ("no data during this period")
                                continue
                            subts_pos0 = np.where(ts == subts[0])[0][0]
                            subds = ds[subts_pos0: subts_pos0 + len(subts)]
            
                            subts2=np.array(subts)-subts[0]
                            f1hz_1s = []
                            i=0
                            dlt=1
                            for i in range(int((subts[-1]-subts[0])//1e9)):
                                ti = subts2[(subts2>i*dlt*1e9)&(subts2<=(i+1)*dlt*1e9)]
                                f1hz_1s.append(len(ti))
                                i = i + 1
                            f1hz_1s2 = np.array(f1hz_1s)  
                            f1hz_1s2 = f1hz_1s2[f1hz_1s2 < cutoffhz]  
            
                            if ((subts[-1]-subts[0])//1e9) > 0:
                                avghz =  (len(subds)/((subts[-1]-subts[0])//1e9))
                            else:
                                continue
                            if len(f1hz_1s2):
                                avghz2= (f1hz_1s2.sum()/len(f1hz_1s2))
                            else:
                                continue
            

                            import matplotlib.pyplot as plt
            
                            # Create a 2x2 grid of subplots
                            fig, axes = plt.subplots(2, 2, figsize=(10, 8))
                            fig.suptitle(dn + dt.strftime(": %Y_%m_%d_%H"))
            
                            # Top-left plot
                            axes[0, 0].scatter(np.arange(len(f1hz_1s)), f1hz_1s, color='red', marker='.')
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
                            #vbinw=10
                            # 1) Build histogram
                            counts, bin_edges = np.histogram(subds, bins=range(min(subds), max(subds)+vbinw, vbinw))
                            # 2) Find local maxima in the counts
                            #    You can tweak `prominence` or `distance` to suit your data.
                            peaks, properties = find_peaks(counts, prominence=20, distance=3)
                            
                            # 3) Compute bin centers for each peak
                            bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
                            peak_centers = bin_centers[peaks]
                            peak_heights = counts[peaks]
    
                            axes[1, 1].hist(subds, bins=range(min(subds), max(subds)+vbinw, vbinw), color='purple')
    
                            for x, h in zip(peak_centers, peak_heights):
                                axes[1,1].axvline(x, color='red', linestyle='--')
                                x = int(x)
                                axes[1,1].annotate(f'{x:d}', 
                                            xy=(x, h), 
                                            xytext=(0, 8), 
                                            textcoords='offset points',
                                            ha='center', color='red')
            
                            axes[1, 1].set_title('Dark Rate Amplitude distribution')
                            axes[1, 1].set_xlabel('Amplitude / ADC bit')
                            axes[1, 1].set_ylabel('Counts')
                            axes[1, 1].set_yscale('log')
                            axes[1, 1].grid()
                           
                            # Adjust layout to prevent overlap
                            plt.tight_layout()
            
                            #plt.show()
                            fig.savefig(pltfp, format='png')
                            plt.close()

                            #write to hdf5 results#################
                            attrsd = {}
                            attrsd["Start_TS"] = subts[0] + ts0
                            attrsd["End_TS"] = subts[-1] + ts0
                            attrsd["Avg"] = avghz
                            attrsd["Avg(<20Hz)"] = avghz2
                            attrsd["Plot_url"] = pltfp
                            dsetd = list(zip(peak_centers, peak_heights))
                            append_data(hdf5_fp=drfp, sipmno=dn, dsetn=dt.strftime("%Y_%m_%d_%H"), dsetd=dsetd, attrsd=attrsd)
    
            append_anaed_fp(hdf5_fp=drfp, anafp=hdf5_fp)

if __name__ == '__main__':
    hdf5_dr_plot_step3()

