# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/19/2025 4:10:58 PM
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
from raw_convertor_trig import RAW_CONV
import struct
import codecs
import pickle
from shutil import copyfile
import shutil
import numpy as np

def raw_pross_step1(rootdir, subdir):
    raw_dir = rootdir + subdir + "/"
    print (raw_dir)
    ana_dir = rootdir + "Ana" + subdir[4:] + "/"
    bak_dir = rootdir + "Bak" + subdir[4:] + "/"
    
    if not os.path.exists(ana_dir):
        try:
            os.makedirs(ana_dir)
        except OSError:
            print ("Error to create folder %s"%ana_dir)
            sys.exit()
    
    if not os.path.exists(bak_dir):
        try:
            os.makedirs(bak_dir)
        except OSError:
            print ("Error to create folder %s"%bak_dir)
            sys.exit()
    
    slicen = 50
    fi = 0
    
    datas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    tdatas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    ch_thrs = [1830, 1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,
               1830, 1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830]
    monitor_flg = True
    tmpi = 0
    while monitor_flg:
        try:
            time.sleep(2)
            for root, dirs, files in os.walk(raw_dir):
                files.sort()
                break
    
            if len(files) > 3:
                tmpi = 0
                pass
            else:
                time.sleep(0.1)
                tmpi =tmpi+ 1
                if tmpi > 12000:
                    tmpi = 0
                    if len(files) == 0:
                        monitor_flg = True
                        break
                    else:
                        monitor_flg = False
                if tmpi % 300 == 0:
                    print ("no new file in 30 seconds!")
                #    break
                continue
        except KeyboardInterrupt:
            print ("Terminated by Ctrl+C ")
            monitor_flg = False
    
    
        #fp = files[fi]
        for fp in files:
            print (fp, "is being procesed!")
            fi = fi + 1
            onefn = raw_dir + fp
            with open (onefn, "rb") as fs:
                rawdata = pickle.load(fs)
            shutil.move(onefn, bak_dir+fp)
    
            for apkg in rawdata:
                chndata, ts, udp_id, ufemb_id,ext_trig_id = rc.raw_conv_per_trig(pkg_data = apkg, total_samN=140)
                for chi in range(32):
                    if ext_trig_id == 1:
                        tdatas[chi].append([ts,chndata[chi]])
                    elif  np.min(chndata[chi][35:50]) < ch_thrs[chi]:
                        datas[chi].append([ts,chndata[chi]])
    
            if (fi%slicen == 0) :
                #save the file
                fn = ana_dir + fp[:-4] + ".ana"
                with open(fn, 'wb') as f:
                    pickle.dump(datas, f)  
                datas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    
                fn = ana_dir + fp[:-4] + ".tana"
                if len(tdatas[0]) > 0:
                    with open(fn, 'wb') as f:
                        pickle.dump(tdatas, f)  
                    tdatas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    
    
        if (monitor_flg == False):
            #save the file
            fn = ana_dir + fp[:-4] + ".ana"
            with open(fn, 'wb') as f:
                pickle.dump(datas, f)  
            datas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    
            fn = ana_dir + fp[:-4] + ".tana"
            if len(tdatas[0]) > 0:
                with open(fn, 'wb') as f:
                    pickle.dump(tdatas, f)  
                tdatas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

rc=RAW_CONV()


rootdir = """G:/SiPM/"""
useddirs = ["Rawdata_20250505_15_57", 
            "Rawdata_20250505_17_45",        
            "Rawdata_20250506_00_00",
            "Rawdata_20250507_00_00",
            "Rawdata_20250508_00_00",
            "Rawdata_20250509_00_00",
            "Rawdata_20250509_12_35",
            "Rawdata_20250509_12_38",
            "Rawdata_20250509_14_28",
            "Rawdata_20250509_14_36",
            "Rawdata_20250509_14_38",
            "Rawdata_20250510_00_00",
            "Rawdata_20250511_00_00",
            "Rawdata_20250512_00_00",
            "Rawdata_20250513_00_00",
            "Rawdata_20250514_00_00",
            "Rawdata_20250515_00_00",
            "Rawdata_20250516_00_00",
            "Rawdata_20250517_00_00",
            "Rawdata_20250518_00_00",
        ]

while True:
    try:
        for root, dirs, files in os.walk(rootdir):
            break
    except OSError:
        continue

    
    subdirs = []
    for rawd in dirs:
        if "Rawdata_" in rawd:
            subdirs.append(rawd)
    
    #subdir = "Rawdata_20250509_14_38/"
    
    
    for subdir in subdirs:
        if subdir not in useddirs:
            raw_pross_step1(rootdir, subdir)
            dates = datetime.now().strftime("%Y%m%d")
            if dates not in subdir:
                useddirs.append(subdir)


