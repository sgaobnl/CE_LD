# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 8/22/2025 9:48:37 AM
"""

import numpy as np
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
    
    # Get all files once
    files = []
    try:
        for root, dirs, file_list in os.walk(raw_dir):
            files = file_list
            break
        files.sort()
    except Exception as e:
        print("Error scanning directory %s: %s" % (raw_dir, str(e)))
        return
    
    if len(files) == 0:
        print("No files to process in %s" % raw_dir)
        return
    
    print("Found %d files to process" % len(files))
    
    # Process all files
    for fp in files:
        print (fp, "is being processed!")
        fi = fi + 1
        onefn = raw_dir + fp
        
        try:
            with open (onefn, "rb") as fs:
                rawdata = pickle.load(fs)
            shutil.move(onefn, bak_dir+fp)
        except Exception as e:
            print("Error processing file %s: %s" % (fp, str(e)))
            continue

        for apkg in rawdata:
            chndata, ts, udp_id, ufemb_id, ext_trig_id = rc.raw_conv_per_trig(pkg_data = apkg, total_samN=140)
            for chi in range(32):
                if ext_trig_id == 1:
                    tdatas[chi].append([ts,chndata[chi]])
                elif np.min(chndata[chi][35:50]) < ch_thrs[chi]:
                    datas[chi].append([ts,chndata[chi]])

        if (fi % slicen == 0):
            # Save the file
            fn = ana_dir + fp[:-4] + ".ana"
            with open(fn, 'wb') as f:
                pickle.dump(datas, f)  
            datas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

            fn = ana_dir + fp[:-4] + ".tana"
            if len(tdatas[0]) > 0:
                with open(fn, 'wb') as f:
                    pickle.dump(tdatas, f)  
                tdatas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

    # Save any remaining data
    if len(datas[0]) > 0:
        fn = ana_dir + fp[:-4] + ".ana"
        with open(fn, 'wb') as f:
            pickle.dump(datas, f)

    if len(tdatas[0]) > 0:
        fn = ana_dir + fp[:-4] + ".tana"
        with open(fn, 'wb') as f:
            pickle.dump(tdatas, f)
    
    print("Finished processing %s" % subdir)


rc = RAW_CONV()

rootdir = """/data/disk1/koloina/raw_data/"""
useddirs = ["Rawdata_20251008_17_33", 
            "Rawdata_20251008_15_22",        
            "Rawdata_20251008_15_58",
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
    
    for subdir in subdirs:
        if subdir not in useddirs:
            raw_pross_step1(rootdir, subdir)
            dates = datetime.now().strftime("%Y%m%d")
            if dates not in subdir:
                useddirs.append(subdir)
    
    # Exit after processing all directories once
    print("All directories processed. Exiting.")
    break
