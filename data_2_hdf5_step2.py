# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/4/2025 5:32:02 PM
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


rootdir = """D:/tmppp/sipm/"""
subdir = "Rawdata_20250502_15_46/"

raw_dir = rootdir + subdir
ana_dir = rootdir + "Ana" + subdir[4:]
rst_dir = rootdir + "Result" + subdir[7:]
bak_dir = rootdir + "Bak" + subdir[4:]

if not os.path.exists(ana_dir):
    print ("folder does not exist")

if not os.path.exists(rst_dir):
    try:
        os.makedirs(rst_dir)
    except OSError:
        print ("Error to create folder %s"%rst_dir)
        sys.exit()


def create_structured_hdf5(hdf5_fp, dtype=np.dtype([("TS","i8"), ("Value", "u2")])):
    if os.path.exists(hdf5_fp):
        pass
        #print("File exists.")   
    else:
        with h5py.File(hdf5_fp, 'w') as f:
            maxshape = (None,)
            for chi in range(32):
                f.create_dataset("CH%02d"%chi, shape=(0,), maxshape=maxshape, dtype=dtype, chunks=True)

            dt = h5py.string_dtype(encoding='utf-8')
            f.create_dataset("file_analyzed", shape=(0,), maxshape=maxshape, dtype=dt, chunks=True)
        print("File and structured datasets created.")

def append_structured_data( hdf5_fp, tdszip,anafp,  dtype=np.dtype([("TS","i8"), ("Value", "u2")]),):
    dt = h5py.string_dtype(encoding='utf-8')
    with h5py.File(hdf5_fp, 'a') as f:
        for chi in range(32):
            newdata = np.array(tdszip[chi], dtype)
            dset = f["CH%02d"%chi]
            old_size = dset.shape[0]
            new_size = newdata.shape[0]
            dset.resize((old_size + new_size,))
            dset[old_size:] = newdata
        nstring = np.array([anafp], dtype=dt)
        dset=f["file_analyzed"]
        old_size = dset.shape[0]
        new_size = nstring.shape[0]
        dset.resize((old_size + new_size,))
        dset[old_size:] = nstring

def filter_anaed_file( hdf5_fp, anafp  ):
    with h5py.File(hdf5_fp, 'r') as f:
        dset=f["file_analyzed"]
        fns = dset[:]
        if anafp.encode('utf-8') in fns:
            return True
        else:
            return False


used_files = []

while True:
    try:  
        for root, dirs, files in os.walk(ana_dir):
            files.sort()
            break

        newfiles = [item for item in files if item not in used_files]
        newfiles = [item for item in newfiles if ".hdf5" not in item]

        if len(newfiles) > 0:
            pass
        elif len(newfiles) == 0:
            print ("no new files, wait 10 seconds...")
            time.sleep(10)
            continue
    except KeyboardInterrupt:
        print ("Terminated by Ctrl+C ")
        exit()

    
    for onef in newfiles:
        fp = ana_dir + onef
        if "uFEMB" in onef :
            pos = onef.find("uFEMB")
            ufemb_id = int(onef[pos+5])
            dr_fp= rst_dir + "uFEMB%d_darkrate.hdf5"%ufemb_id
            tg_fp= rst_dir + "uFEMB%d_trigger.hdf5"%ufemb_id
            create_structured_hdf5(hdf5_fp=dr_fp)
            create_structured_hdf5(hdf5_fp=tg_fp)


        if (".ana" in onef) or (".tana" in onef): 
            if (".ana" in onef) :
                hdf5_fp = dr_fp
            elif (".tana" in onef): 
                hdf5_fp = tg_fp
    
            if filter_anaed_file(hdf5_fp=hdf5_fp, anafp=onef  ):
                used_files.append(onef)
                print (onef, " was analyzed, ignore...")
                continue
    
            tdszip = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
            with open (fp, "rb") as fs:
                print (fp)
                datas = pickle.load(fs)
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
                            tdszip[chi].append((datas[chi][xi][0]*10+np_pos*500, abs(ped-namp)))
            append_structured_data(hdf5_fp=hdf5_fp, anafp=onef, tdszip=tdszip)
    

#from scipy.signal import find_peaks 
#tss = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
#dss = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

#import matplotlib.pyplot as plt
#plt.plot(np.array(tss[1])/1e9,dss[1])
#plt.show()
#plt.close()

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

