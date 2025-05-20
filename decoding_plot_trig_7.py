# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/13/2025 5:19:19 PM
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


fn = "G:/SiPM/xxx/uFEMB1_20250513_17_11_00000000000000000035478963124720.bin"
with open (fn, "rb") as fs:
    trigs_all = pickle.load(fs)

#for fech in [49, 50, 51, 52, 53, 54]:
#for fech in range(32):
for fech in range(0,32,1):
    #if fech in [32,39,40,47,48,55,56,63]:
    if fech in [0,16]:
       continue
    trigs=trigs_all[fech]
#for fech in [53, 54]:
#for fech in [53]:
    k = 0
    trigns = []
#    import matplotlib.pyplot as plt
    for trig in trigs:
        rms1 = np.std(trig[00:30])
        rms2 = np.std(trig[100:])
        if rms2 < rms1:
            ped = int(np.mean(trig[0:30]))
        else:
            ped = int(np.mean(trig[100:]))
            
        trign = ped-np.min(trig[40:50])
        if trign > 20 :
            trigns.append(trign)
#            plt.plot(trig)
            k = k + 1
#    plt.show()
#    plt.close()
    
    print (k, len(trigs), k/len(trigs))
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(16,8))
    plt.hist(trigns, bins=range(min(trigns), max(trigns)+10, 10))
    plt.title ("CH%02d, rate=%.2f%%"%(fech, k*100/len(trigs)))
    plt.xlim((0,2000))
    plt.grid()
    plt.show()
    plt.close()

exit()


#rawdir = """C:/uFEMB\SiPM/Rawdata_20250417_14_31/"""
##fn = rawdir + "uFEMB2_00000000000000000000000183318435.bin"
#
#rawdir = """C:/uFEMB/SiPM/"""
#print ("##################################")
#for root, dirs, files in os.walk(rawdir):
#    t = datetime.now().strftime("%Y%m%d")
#    t = "20250417_14_31"
#    dirs_today = [] 
#    for onedir in dirs:
#        if t in onedir:
#            dirs_today.append(onedir)
#    dirs_today.sort(reverse = True)
#    break
#latest_dir = rawdir + dirs_today[0] + "/"
#print (latest_dir)
#for root, dirs, files in os.walk( latest_dir):
#    files.sort(reverse = True)
#    break
#
##if len(files) < 1 :
##    print ("no file under the folder")
##    exit()
##elif len(files) == 1 :
##    onefile = files[0]
##else:
##    print (len(files))
##    onefile = files[1]
#
#print ("##################################")
#trigs = []
#for onefile in files[0:20]:
#    onefn = latest_dir + onefile
#    print (onefile)
#    
#    with open (onefn, "rb") as fs:
#        rawdata = pickle.load(fs)
#    
#    rc = RAW_CONV()
#    sipmorders = ["A1", "A3", "A5", "A6", "A4", "A2"]
#    
#    for apkg in rawdata:
#        try:
#            chndata, ts, udp_id, ufemb_id = rc.raw_conv_per_trig(pkg_data = apkg, total_samN=140)
#            ch = 49 
#            trigs.append(chndata[ch-32])
#            
##            import matplotlib.pyplot as plt
##            fig = plt.figure(figsize=(16,8))
##            #print ("P6####")
##            for ch in [49, 50, 51, 52, 53, 54]:
##            #for ch in [49]:
##                i = ch-32
##                if ch in [49, 50, 51, 52, 53, 54]:
##                    rmsch = np.std(chndata[i][80:])
##                    peakp = np.max(chndata[i])
##                    plt.plot(chndata[i], marker = 's', label="P6_%s_ch%d_rms%.3f_peak%d"%(sipmorders[ch-49], ch, rmsch, peakp))
##    
##            #print ("P7####")
##            #for ch in [57, 58, 59, 60, 61, 62]:
##            for ch in []:
##                i = ch-32
##                if ch in [57, 58, 59, 60, 61, 62]:
##                    rmsch = np.std(chndata[i][80:])
##                    peakp = np.max(chndata[i])
##                    plt.plot(chndata[i], marker = 'o',label="P7_%s_ch%d_rms%.3f_peak%d"%(sipmorders[ch-57], ch, rmsch, peakp))
##            plt.legend(loc=1,fontsize=18)
##            plt.grid()
##            plt.title(dirs_today[0])
##            plt.show()
##            plt.close()
#        except KeyboardInterrupt:
#            print ("End the process! ")
#            exit()

#import pickle
#fn = """C:/uFEMB/SiPM/data_ch49.bin"""
#with open(fn, "wb") as fp:
#    pickle.dump(trigs, fp)
#exit()
fn = """C:/uFEMB/SiPM/data_ch5320250422_11_32.bin"""
with open (fn, "rb") as fs:
    trigs = pickle.load(fs)
print (len(trigs))

k = 0
trigps = []
trigns = []
import matplotlib.pyplot as plt
for trig in trigs:
    ped1 = np.std(trig[00:30])
    ped2 = np.std(trig[100:])
    if ped2 < ped1:
        ped = int(np.mean(trig[0:30]))
    else:
        ped = int(np.mean(trig[100:]))

    trigp = ped-np.max(trig[44:46])
    trign = ped-np.min(trig[44:46])
    #plt.plot(trig)
    if trign > 200 :
        #trigps.append(trigp)
        trigps.append(trign)
        #if np.min(trig[70:]) < 
        plt.plot(trig)
        k = k + 1
    #if  trign < 1850:
    #    trigns.append(trign)
        #plt.plot(trig)
    #    k = k + 1
plt.grid()
plt.show()
plt.close()

print (k, len(trigs), k/len(trigs))
import matplotlib.pyplot as plt
plt.hist(trigps, bins=range(min(trigps), max(trigps)+5, 5))
#plt.hist(trigns, bins=range(min(trigns), max(trigns)+5, 5))
#plt.hist(trigns)
#print (trigps, trigns)
plt.grid()
plt.show()
plt.close()

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

