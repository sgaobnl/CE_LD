# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/2/2025 5:08:54 PM
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
import shutil
import numpy as np

rc = RAW_CONV()

rootdir = """D:/tmppp/sipm/"""
subdir = "Rawdata_20250501_11_38/"
raw_dir = rootdir + subdir
ana_dir = rootdir + "Ana" + subdir[4:]
bak_dir = rootdir + "Bak" + subdir[4:]
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
        for root, dirs, files in os.walk(raw_dir):
            files.sort()
            break

        if len(files) > 3:
            pass
        else:
            time.sleep(0.1)
            tmpi =tmpi+ 1
            if tmpi > 10:
                print ("no new file in a second!")
                tmpi = 0
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



#for chi in range(32):
#    import matplotlib.pyplot as plt
#    if len(datas[chi])> 0:
#        for xi in range(len(datas[chi])):
#            ts=datas[chi][xi][0]
#            data=datas[chi][xi][1]
#            x=np.arange(ts*10, ts*10+len(data)*500, 500)
#            plt.plot(x/1e9,data)
#    plt.show()
#    plt.close()

#                plt.title("%d"%chi)
#                plt.show()
#                plt.close()
#        print (ts-t0, udp_id, ufemb_id)
#        t0 = ts
#    input()



#    try:
#        chndata, ts, udp_id, ufemb_id = rc.raw_conv_per_trig(pkg_data = apkg, total_samN=140)
#        import matplotlib.pyplot as plt
#        fig = plt.figure(figsize=(16,8))
#        #for ch in [1,2,3,4,5,6]:
#        #for ch in range(20,32,1):
#        #for ch in range(20):
#        for ch in range(32):
#            i = ch-0
#            rmsch = np.std(chndata[i][80:])
#            meanch = np.mean(chndata[i])
#            peakn = np.min(chndata[i])
#            #plt.plot(chndata[i], marker = '^', label="P1_%s_ch%d_rms%.3f_peak%d"%(sipmorders[ch-1], ch, rmsch, peakp ))
#            plt.plot(chndata[i], marker = '^', label="ch%d_rms%.3f_peak%d"%( ch, rmsch, peakn ))
#            print (i, rmsch, meanch, meanch-10*rmsch, peakn)
#        plt.legend(loc=1, fontsize=10)
#        plt.grid()
#        plt.title(dirs_today[0] + ":" + onefile)
#        plt.show()
#        plt.close()
#        #break
#    except KeyboardInterrupt:
#        print ("End the process! ")
#        exit()
#
    

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

