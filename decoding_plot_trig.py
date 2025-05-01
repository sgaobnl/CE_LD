# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/1/2025 11:51:50 AM
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
from fft_chn import chn_fft

#rawdir = """D:/uFEMB\Rawdata/SiPM/"""
#rawdir = """D:/uFEMB/SiPM/Rawdata_20250416_15_55/"""
#fn = rawdir + "uFEMB1_00000000000000000000000897318436.bin"

while True:
    rawdir = """D:/uFEMB/SiPM/"""
    print ("##################################")
    for root, dirs, files in os.walk(rawdir):
        #t = datetime.now().strftime("%Y%m%d")
        t = "20250501_11_42"
        dirs_today = [] 
        for onedir in dirs:
            if t in onedir:
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
        
        #exit()
    #elif len(files) == 1 :
    #    onefile = files[0]
    else:
        onefile = files[0]
    onefile = "uFEMB1_00000000000000000000002974445468.bin"
    
    print (onefile)
    print ("##################################")
    onefn = latest_dir + onefile
    
    
    with open (onefn, "rb") as fs:
        rawdata = pickle.load(fs)
    
    rc = RAW_CONV()
    sipmorders = ["A1", "A3", "A5", "A6", "A4", "A2"]
    
    for apkg in rawdata:
        try:
            chndata, ts, udp_id, ufemb_id = rc.raw_conv_per_trig(pkg_data = apkg, total_samN=140)
            import matplotlib.pyplot as plt
            fig = plt.figure(figsize=(16,8))
            #for ch in [1,2,3,4,5,6]:
            #for ch in range(20,32,1):
            #for ch in range(20):
            for ch in range(32):
                i = ch-0
                rmsch = np.std(chndata[i][80:])
                meanch = np.mean(chndata[i])
                peakn = np.min(chndata[i])
                #plt.plot(chndata[i], marker = '^', label="P1_%s_ch%d_rms%.3f_peak%d"%(sipmorders[ch-1], ch, rmsch, peakp ))
                plt.plot(chndata[i], marker = '^', label="ch%d_rms%.3f_peak%d"%( ch, rmsch, peakn ))
                print (i, rmsch, meanch, meanch-10*rmsch, peakn)
            plt.legend(loc=1, fontsize=10)
            plt.grid()
            plt.title(dirs_today[0] + ":" + onefile)
            plt.show()
            plt.close()
            #break
        except KeyboardInterrupt:
            print ("End the process! ")
            exit()

    

#import matplotlib.pyplot as plt
#rmss = []
#for i in range(32):
#    print (np.std(chn_data[i]), i, np.mean(chn_data[i]))
#    rmss.append(np.std(chn_data[i]))
#plt.plot(rmss,marker='.' )
#plt.show()
#plt.close()
#exit()


#pd = 500
#chn_data_avgs = []
#
#import matplotlib.pyplot as plt
##for ch in [224 ,25, 26, 27, 28, 29, 30, 31]:
##for ch in range(32):
#for ch in range(1,5):
#    chn_data[ch] = chn_data[ch][100:]
#    for avgi in range(500):
#        if avgi == 0:
#            chn_data_avg = np.array(chn_data[ch][0:pd])
#        else:
#            chn_data_avg = chn_data_avg + np.array(chn_data[ch][avgi*pd:(avgi+1)*pd])
#    chn_data_avg = chn_data_avg/500
#    chn_data_avg = chn_data_avg - np.mean(chn_data_avg)
#        
#    plt.plot(chn_data_avg,marker='.', label="CH%d"%ch )
#plt.grid()
#plt.legend(loc=1)
#plt.show()
#plt.close()

#import matplotlib.pyplot as plt
#rmss = []
#for i in range(32):
#    print (np.std(chn_data[i]), i, np.mean(chn_data[i]))
#    rmss.append(np.std(chn_data[i]))
#plt.plot(rmss,marker='.' )
#plt.show()
#plt.close()
#for i in range(32):
##for i in [30]:
#    fig = plt.figure(figsize=(8,6))
#    plt.rcParams.update({'font.size': 18})
##    plt.plot(chn_data[i], label="Ch%d"%i )
#    print (len(chn_data[i]))
##    f,p = chn_fft(chn_data[i], fft_s=5000 )
#    plt.plot(f,p)
#    plt.legend()
#    plt.show()

