# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 6/28/2023 9:52:59 AM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
import numpy as np
import struct
import os
from sys import exit
import os.path
import math
import copy
import pickle

fn_map = "./SBND_mapping.csv"
dec_chn = []
with open (fn_map, 'r') as fp:
    for cl in fp:
        if "\n" in cl:
            cl = cl.replace("\n", "")
        tmp = cl.split(",")
        x = []
        for i in tmp:
            x.append(i.replace(" ", ""))
        dec_chn.append(x)
dec_chn = dec_chn[1:]
lendec = len(dec_chn)
print (lendec)


rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/chk_post_bolt/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_SHV5V/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_a_short/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_a_coupling/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_noSHVcable/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_SHV5V/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_SHV1V/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_noSHVcable/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_SHVOFF/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/chk_pre_bolt/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/RMS20us/"""
rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/RMS20usHV1V/"""
#rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/RMS20usHVoff/"""

chk_fns = []
for root, dirs, files in os.walk(rawdir):
    for fn in files:
        if "FEMB_CHKOUT_" in fn:
            chk_fns.append(fn)
    break

for fn in chk_fns:
    with open (rawdir + fn, "rb") as fs:
        raw_data = pickle.load(fs)
        for fembi in range(4):
            qc_list = raw_data[fembi][0]
            qc_pf = qc_list[0]
            femb_id = qc_list[2]
            femb_rerun_f = qc_list[3]
            map_r = raw_data[fembi][1]
            #if fembi<2: #check tp status
            #    print ( raw_data[fembi][3][14],  raw_data[fembi][3][17],  raw_data[fembi][3][18])
            if map_r != None:
                map_pf =  map_r[0]
                map_pf_str = map_r[1]
                chn_rmss = map_r[2][0] # 128chn list, each element is a integal
                chn_peds = map_r[2][1] # 128chn list, each element is a float
                chn_pkps = map_r[2][2] # 128chn list, each element is a integal
                chn_pkns = -(abs(np.array(map_r[2][3]))) # 128chn list, each element is a integal
                if "PASS" in qc_pf:
                    crateno = int(femb_id[5])
                    wibno   = int(femb_id[14])
                    fembno   = int(femb_id[23])
                    for i in range(lendec):
                        if (int(dec_chn[i][5]) == crateno) and (int(dec_chn[i][6]) == wibno ) and (int(dec_chn[i][7]) == fembno ) :
                            decch = int(dec_chn[i][8])
                            dec_chn[i].append(chn_rmss[decch])
                            dec_chn[i].append(chn_peds[decch])
                            dec_chn[i].append(chn_pkps[decch])
                            dec_chn[i].append(chn_pkns[decch])
        raw_data = None

e_yrmss = []
e_urmss = []
e_vrmss = []
e_ypeds = []
e_upeds = []
e_vpeds = []
e_ypkps = []
e_upkps = []
e_vpkps = []
e_ypkns = []
e_upkns = []
e_vpkns = []

w_yrmss = []
w_urmss = []
w_vrmss = []
w_ypeds = []
w_upeds = []
w_vpeds = []
w_ypkps = []
w_upkps = []
w_vpkps = []
w_ypkns = []
w_upkns = []
w_vpkns = []

for chn in range(1,1986):
    for i in range(lendec):
        if (int(dec_chn[i][10]) == chn):
            if (int(dec_chn[i][5]) <= 2): #west apa
                if len(dec_chn[i])>12:
                    if "U" in dec_chn[i][9]:
                        w_urmss.append( dec_chn[i][12])
                        w_upeds.append( dec_chn[i][13])
                        w_upkps.append( dec_chn[i][14])
                        w_upkns.append( dec_chn[i][15])
                    if "V" in dec_chn[i][9]:
                        w_vrmss.append( dec_chn[i][12])
                        w_vpeds.append( dec_chn[i][13])
                        w_vpkps.append( dec_chn[i][14])
                        w_vpkns.append( dec_chn[i][15])
                    if "Y" in dec_chn[i][9]:
                        w_yrmss.append( dec_chn[i][12])
                        w_ypeds.append( dec_chn[i][13])
                        w_ypkps.append( dec_chn[i][14])
                        w_ypkns.append( dec_chn[i][15])
            else:#east apa
                if len(dec_chn[i])>12:
                    if "U" in dec_chn[i][9]:
                        e_urmss.append( dec_chn[i][12])
                        e_upeds.append( dec_chn[i][13])
                        e_upkps.append( dec_chn[i][14])
                        e_upkns.append( dec_chn[i][15])
                    if "V" in dec_chn[i][9]:
                        e_vrmss.append( dec_chn[i][12])
                        e_vpeds.append( dec_chn[i][13])
                        e_vpkps.append( dec_chn[i][14])
                        e_vpkns.append( dec_chn[i][15])
                    if "Y" in dec_chn[i][9]:
                        e_yrmss.append( dec_chn[i][12])
                        e_ypeds.append( dec_chn[i][13])
                        e_ypkps.append( dec_chn[i][14])
                        e_ypkns.append( dec_chn[i][15])
#    break
result = [
            ["EU", e_urmss, e_upeds, e_upkps, e_upkns],
            ["Ev", e_vrmss, e_vpeds, e_vpkps, e_vpkns],
            ["EY", e_yrmss, e_ypeds, e_ypkps, e_ypkns],
            ["WU", w_urmss, w_upeds, w_upkps, w_upkns],
            ["Wv", w_vrmss, w_vpeds, w_vpkps, w_vpkns],
            ["WY", w_yrmss, w_ypeds, w_ypkps, w_ypkns]
         ]

fr =rawdir + "test_results"+".result" 
with open(fr, 'wb') as f:
    pickle.dump(result, f)

print (len(w_urmss),len(w_vrmss), len(w_yrmss), len(e_urmss),len(e_vrmss), len(e_yrmss)  )
exit()
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_urmss)) + 1
plt.plot(x, w_urmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_urmss)) + 1
plt.plot(x, e_urmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_vrmss)) + 1
plt.plot(x, w_vrmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_vrmss)) + 1
plt.plot(x, e_vrmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_yrmss)) + 1
plt.plot(x, w_yrmss)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_yrmss)) + 1
plt.plot(x, e_yrmss)
plt.show()
plt.close()
exit()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_upeds)) + 1
plt.plot(x, w_upeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_upeds)) + 1
plt.plot(x, e_upeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_vpeds)) + 1
plt.plot(x, w_vpeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_vpeds)) + 1
plt.plot(x, e_vpeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(w_ypeds)) + 1
plt.plot(x, w_ypeds)
plt.show()
plt.close()

fig = plt.figure(figsize=(8.5,11))
x = np.arange(len(e_ypeds)) + 1
plt.plot(x, e_ypeds)
plt.show()
plt.close()


#    femb_date = qc_list[4]
#    print(qc_pf)
#    print(env)
#    print(femb_id)
#    print(femb_rerun_f)
#    print(femb_date)

  #  break
    

