# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 8/22/2025 10:00:24 AM
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
from raw_convertor_trig import RAW_CONV
import pickle
from shutil import copyfile
import numpy as np

while True:
    
    rawdir = """G:/SiPM/"""
    print ("##################################")
    for root, dirs, files in os.walk(rawdir):
        t = datetime.now().strftime("%Y%m%d")
        dirs_today = [] 
        for onedir in dirs:
            if (t in onedir) and ("Rawdata_" in onedir):
                dirs_today.append(onedir)
        dirs_today.sort(reverse = True)
        break
    latest_dir = rawdir + dirs_today[0] + "/"
    print (latest_dir)
    for root, dirs, files in os.walk( latest_dir):
        files.sort(reverse = True)
        break
    
    if len(files) < 1 :
        print ("no file under the folder")
        time.sleep(1)
    else:
        onefile = files[0]
    
    print (onefile)
    print ("##################################")
    onefn = latest_dir + onefile
    
    
    try:
        with open (onefn, "rb") as fs:
            rawdata = pickle.load(fs)
    except FileNotFoundError:
        print ("Wait 5 seconds")
        time.sleep(5)
        continue
    
    rc = RAW_CONV()
    
    for apkg in rawdata:
        try:
            chndata, ts, udp_id, ufemb_id, ext_trigger = rc.raw_conv_per_trig(pkg_data = apkg, total_samN=140)
            
            plt_flg = True

            if plt_flg:
                import matplotlib.pyplot as plt
                fig = plt.figure(figsize=(16,8))
                #for ch in range(0+(ufemb_id-1)*32,0+(ufemb_id-1)*32+32,1): #for all 32 chns
                #for ch in [0]: #ch0
                for ch in range(32):
                    if ch >=32:
                        i = ch-32
                    else:
                        i = ch
                    if True:
                        rmsch = np.std(chndata[i][0:30])
                        meanch = int(np.mean(chndata[i]))
                        peakn = meanch - np.min(chndata[i])
                        if peakn > 50:
                            plt.plot(chndata[i], marker = 's', label="ch%d_rms%.3f_mean%d_amp%d_ext%d"%( ch, rmsch, meanch,peakn, ext_trigger))
                plt.legend(loc=1,fontsize=10)
                plt.grid()
                plt.title(dirs_today[0] + ":" + onefile)
                plt.show()
                plt.close()
                break
        except KeyboardInterrupt:
            print ("End the process! ")
            exit()
