# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 8/22/2025 9:48:37 AM
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
            "Rawdata_20250519_00_00",
            "Rawdata_20250520_00_00",
            "Rawdata_20250521_00_00",
            "Rawdata_20250522_00_00",
            "Rawdata_20250523_00_00",
            "Rawdata_20250524_00_00",
            "Rawdata_20250525_00_00",
            "Rawdata_20250526_00_00",
            "Rawdata_20250527_00_00",
            "Rawdata_20250528_00_00",
            "Rawdata_20250529_00_00",
            "Rawdata_20250530_00_00",
            "Rawdata_20250531_00_00",
            "Rawdata_20250601_00_00",
            "Rawdata_20250602_00_00",
            "Rawdata_20250603_00_00",
            "Rawdata_20250604_00_00",
            "Rawdata_20250605_00_00",
            "Rawdata_20250606_00_00",
            "Rawdata_20250607_00_00",
            "Rawdata_20250608_00_00",
            "Rawdata_20250609_00_00",
            "Rawdata_20250610_00_00",
            "Rawdata_20250611_00_00",
            "Rawdata_20250612_00_00",
            "Rawdata_20250613_00_00",
            "Rawdata_20250614_00_00",
            "Rawdata_20250615_00_00",
            "Rawdata_20250616_00_00",
            "Rawdata_20250617_00_00",
            "Rawdata_20250618_00_00",
            "Rawdata_20250619_00_00",
            "Rawdata_20250620_00_00",
            "Rawdata_20250621_00_00",
            "Rawdata_20250622_00_00",
            "Rawdata_20250623_00_00",
            "Rawdata_20250624_00_00",
            "Rawdata_20250625_00_00",
            "Rawdata_20250626_00_00",
            "Rawdata_20250627_00_00",
            "Rawdata_20250628_00_00",
            "Rawdata_20250629_00_00",
            "Rawdata_20250630_00_00",
            "Rawdata_20250701_00_00",
            "Rawdata_20250702_00_00",
            "Rawdata_20250703_00_00",
            "Rawdata_20250704_00_00",
            "Rawdata_20250705_00_00",
            "Rawdata_20250706_00_00",
            "Rawdata_20250707_00_00",
            "Rawdata_20250708_00_00",
            "Rawdata_20250709_00_00",
            "Rawdata_20250710_00_00",
            "Rawdata_20250711_00_00",
            "Rawdata_20250712_00_00",
            "Rawdata_20250713_00_00",
            "Rawdata_20250714_00_00",
            "Rawdata_20250715_00_00",
            "Rawdata_20250716_00_00",
            "Rawdata_20250717_00_00",
            "Rawdata_20250718_00_00",
            "Rawdata_20250719_00_00",
            "Rawdata_20250720_00_00",
            "Rawdata_20250721_00_00",
            "Rawdata_20250722_00_00",
            "Rawdata_20250723_00_00",
            "Rawdata_20250724_00_00",
            "Rawdata_20250725_00_00",
            "Rawdata_20250726_00_00",
            "Rawdata_20250727_00_00",
            "Rawdata_20250728_00_00",
            "Rawdata_20250729_00_00",
            "Rawdata_20250730_00_00",
            "Rawdata_20250731_00_00",
            "Rawdata_20250800_00_00",
            "Rawdata_20250801_00_00",
            "Rawdata_20250802_00_00",
            "Rawdata_20250803_00_00",
            "Rawdata_20250804_00_00",
            "Rawdata_20250805_00_00",
            "Rawdata_20250806_00_00",
            "Rawdata_20250807_00_00",
            "Rawdata_20250808_00_00",
            "Rawdata_20250809_00_00",
            "Rawdata_20250810_00_00",
            "Rawdata_20250811_00_00",
            "Rawdata_20250812_00_00",
            "Rawdata_20250813_00_00",
            "Rawdata_20250814_00_00",
            "Rawdata_20250815_00_00",
            "Rawdata_20250816_00_00",
            "Rawdata_20250817_00_00",
            "Rawdata_20250818_00_00",
            "Rawdata_20250819_00_00",
            "Rawdata_20250820_00_00",


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


