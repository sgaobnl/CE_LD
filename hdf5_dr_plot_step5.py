# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/19/2025 12:42:13 PM
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


fm = """D:/GitHub/CE_LD/chn_mapping.csv"""
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
subdir = "Rawdata_20250519_00_00/"

raw_dir = rootdir + subdir
ana_dir = rootdir + "Ana" + subdir[4:]
rst_dir = rootdir + "Result" + subdir[7:]
bak_dir = rootdir + "Bak" + subdir[4:]

if not os.path.exists(rst_dir):
    print ("folder does not exist")
    exit()

for ufemb_id in [1,2]:
    hdf5_fp=rst_dir + "ufemb%d_%s_darkrate.hdf5"%(ufemb_id, subdir[8:16])
    print (hdf5_fp)
    if os.path.isfile(hdf5_fp):    
        pass
    else:
        continue


    with h5py.File(hdf5_fp, "r") as f:
        for ch in range(32):
    
            key = "CH%02d"%ch
            dn = dmap[(ufemb_id-1)*32+ch]
            print (dn)
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
    
                ts = np.array(ts)
    
    #            ts = ts-ts[0]
                tlen = int(ts[-1])
                cutoffhz=20
                vbinw=10
    
                for hi in range (int(tlen//(1e9*h2s))):
                    print ("hour of ", hi)
                    subts = ts[(ts>hi*h2s*1e9)&(ts<=(hi+1)*h2s*1e9)]
                    if len(subts) <= 0:
                        print ("no data during this period")
                        continue
                    subts_pos0 = np.where(ts == subts[0])[0][0]
                    subds = ds[subts_pos0: subts_pos0 + len(subts)]
    
                    subts2=np.array(subts)-subts[0]
                    f1hz_1s = []
                    i=0
                    dlt=1
                    for i in range(h2s):
                        ti = subts2[(subts2>i*dlt*1e9)&(subts2<=(i+1)*dlt*1e9)]
                        f1hz_1s.append(len(ti))
                        i = i + 1
                    f1hz_1s2 = np.array(f1hz_1s)  
                    f1hz_1s2 = f1hz_1s2[f1hz_1s2 < cutoffhz]  
    
                    avghz =  (len(subts)/3600)
                    avghz2= (f1hz_1s2.sum()/len(f1hz_1s2))
    
    
    
                    import matplotlib.pyplot as plt
    
                    # Create a 2x2 grid of subplots
                    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
                    fig.suptitle(dn + ": Hour#%d"%hi)
    
                    # Top-left plot
                    axes[0, 0].scatter(np.arange(h2s), f1hz_1s, color='red', marker='.')
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
                    axes[1, 1].hist(subds, bins=range(min(subds), max(subds)+vbinw, vbinw), color='purple')
                    axes[1, 1].set_title('Dark Rate Amplitude distribution')
                    axes[1, 1].set_xlabel('Amplitude / ADC bit')
                    axes[1, 1].set_ylabel('Counts')
                    axes[1, 1].set_yscale('log')
                    axes[1, 1].grid()
                    
                    # Adjust layout to prevent overlap
                    plt.tight_layout()
                    pltfp = plt_dir + "ufemb%d_CH%d_Hour%04d.png"%(ufemb_id,ch, hi)
    
                    fig.savefig(pltfp, format='png')
                   
               # Show the figure
               #plt.show()


#                #plt.scatter(ts[1000:], ds[1000:], marker='.')
#            #    plt.plot(ts[0:10], ds[0:10], color='r')
#
#                #plt.scatter(np.array(subts)/1e9, subds, marker='.')
#                plt.hist(subds, bins=range(min(subds), max(subds)+vbinw, vbinw))
#
#                #plt.plot(f1hz_1s, marker='.')
##                plt.hist(f1hz_1s, bins=range(min(f1hz_1s), max(f1hz_1s)+1, 1))
##                plt.hist(f1hz_1s2, bins=range(min(f1hz_1s2), max(f1hz_1s2)+1, 1))
#                
#
#                plt.show()

#            import matplotlib.pyplot as plt
#            plt.scatter(ts, ds, marker='.')
#            plt.show()
#            plt.close()
#
#            print (len(ts))
#            exit()

#                ki = ki+len(ti)

#            ki=0
#            while ki < len(ts):
#                ti = ts[(ts>ki*1)&(ts<=(ki+1)*1e9)]
#                print (ki)
#                f1hz_1s.append(len(ti))
#                ki = ki+len(ti)
#            #plt.scatter(ts, ds, marker='.')
#            import matplotlib.pyplot as plt
#            #plt.plot(f1hz_1s, marker='.')
#            plt.plot(f1hz_01s, marker='.')
#            #plt.hist(f1hz_1s, bins=range(min(f1hz_1s), max(f1hz_1s)+1, 1))
#            #plt.hist(f1hz_01s, bins=range(min(f1hz_01s), max(f1hz_01s)+1, 1))
#            plt.show()
#            plt.close()
#
#
#
#            print (ts[0:100])
#            exit()
#
##    ks = []
##    for i in range(len(ds)):
##        if ds[i] == 0xffff:
##            ks.append(0)
##        else:
##            ks.append(ds[i])
##    ds = ks
#    import matplotlib.pyplot as plt
#    plt.scatter(ts[1000:], ds[1000:], marker='.')
##    plt.plot(ts[0:10], ds[0:10], color='r')
#    plt.show()
#    plt.close()

exit()

#from scipy.signal import find_peaks 
#tss = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
#dss = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
tdszip = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

for onef in files:
    fp = ana_dir + onef
    if ".ana" in onef: #dark data
        with open (fp, "rb") as fs:
            datas = pickle.load(fs)
            print (onef)
            for chi in range(32):
                if len(datas[chi])> 0:
                    ts = []
                    ds = []
                    for xi in range(len(datas[chi])):
                        if xi == 0:
                            ped = int(np.mean(datas[chi][xi][1][0:30]))
                        td = np.array(datas[chi][xi][1][40:60])
                        namp = np.min(td) 
                        np_pos = np.where( td== namp)[0][0]
                        tdszip[chi].append((datas[chi][xi][0]*10+np_pos*500, ped-namp))
            append_structured_data(hdf5_fp=rootdir + subdir + "xx.hdf5", tdszip=tdszip)
                    #    ts.append(datas[chi][xi][0]*10+np_pos*500)
                        #print (datas[chi][xi][0]*10+np_pos*500)
                    #    ds.append(ped-namp)
                    #tss[chi] +=ts
                    #dss[chi] +=ds
    


                #ts=datas[chi][xi][0]
                #data=datas[chi][xi][1]
                #x=np.arange(ts*10, ts*10+len(data)*500, 500)
                #plt.plot(x/1e9,data)
#            plt.plot(np.array(ts)/1e9,ds)
#            plt.show()
#            plt.close()
    

##from scipy.signal import find_peaks 
#for onef in files:
#    fp = ana_dir + onef
#    if ".ana" in onef: #dark data
#        with open (fp, "rb") as fs:
#            datas = pickle.load(fs)
#
#    for chi in range(32):
#        if len(datas[chi])> 0:
#            for xi in range(len(datas[chi])):
#                ts=datas[chi][xi][0]
#                data=datas[chi][xi][1]
#                x=np.arange(ts*10, ts*10+len(data)*500, 500)
#                import matplotlib.pyplot as plt
#                #plt.plot(x/1e9,data)
#                data = np.array(data)
#                peaks, _= find_peaks(-data, threshold=50) 
#                print (peaks)
#                if len(peaks) > 1:
#                    plt.plot(data)
#                    plt.show()
#                    plt.close()
#

exit()

slicen = 50
fi = 0

datas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
tdatas=[[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
ch_thrs = [1830, 1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,
           1830, 1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830,1830]
monitor_flg = True
tmpi = 0
while monitor_flg:

    for root, dirs, files in os.walk(raw_dir):
        files.sort()
        break

    if len(files) > 3:
        pass
    else:
        try:
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

