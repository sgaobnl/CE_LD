# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/1/2025 11:34:43 AM
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

#rawdir = """C:/uFEMB/SiPM/Rawdata_20250421_15_42/"""
#fn = rawdir + "uFEMB2_00000000000000000000000183318435.bin"

rawdir = """D:/uFEMB/SiPM/"""
print ("##################################")
for root, dirs, files in os.walk(rawdir):
    t = datetime.now().strftime("%Y%m%d")
    t = "20250501_11_34"
    ttmp = t
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

#if len(files) < 1 :
#    print ("no file under the folder")
#    exit()
#elif len(files) == 1 :
#    onefile = files[0]
#else:
#    print (len(files))
#    onefile = files[1]

print ("##################################")
trigs = [[], [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
for onefile in files[0:20]:
    onefn = latest_dir + onefile
    print (onefile)
    
    with open (onefn, "rb") as fs:
        rawdata = pickle.load(fs)
    
    rc = RAW_CONV()
    sipmorders = ["A1", "A3", "A5", "A6", "A4", "A2"]
    
    for apkg in rawdata:
        try:
            chndata, ts, udp_id, ufemb_id = rc.raw_conv_per_trig(pkg_data = apkg, total_samN=140)
            for ki in range(32):
                trigs[ki].append(chndata[ki])
            
        except KeyboardInterrupt:
            print ("End the process! ")
            exit()

import pickle
fn = rawdir + "/data_" + ttmp + """.bin"""
with open(fn, "wb") as fp:
    pickle.dump(trigs, fp)


exit()

import matplotlib.pyplot as plt
k = 0
trigps = []
trigns = []
for trig in trigs:
    trigp = np.max(trig[44:46])
    trign = np.min(trig[44:46])
    plt.plot(trig)
    if trigp > 1950 :
        trigps.append(trigp)
   #     plt.plot(trig)
        k = k + 1
    if  trign < 1850:
        trigns.append(trign)
   #     plt.plot(trig)
        k = k + 1
print (k, len(trigs), k/len(trigs))
#print (trigps, trigns)
plt.grid()
plt.show()
plt.close()
import matplotlib.pyplot as plt

print (len(trigs))
    
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

