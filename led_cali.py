# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 6/2/2025 12:04:00 PM
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
        for fn in fns:
            if anafp in str(fn):
                return True
        return False


def STEP2(rootdir, subdir):

    ana_dir = rootdir + "Ana" + subdir[4:] + "/"
    rst_dir = rootdir + "Result" + subdir[7:] + "/"
    bak_dir = rootdir + "Bak" + subdir[4:] + "/"
    
    if not os.path.exists(ana_dir):
        print ("folder does not exist")
    
    if not os.path.exists(rst_dir):
        try:
            os.makedirs(rst_dir)
        except OSError:
            print ("Error to create folder %s"%rst_dir)
            sys.exit()

    if True:
        print (ana_dir)
        newfiles=[]
        for root, dirs, files in os.walk(ana_dir):
            files.sort()
            newfiles = files
            break

        if len(newfiles) > 0:
            newfiles = [item for item in newfiles if ".hdf5" not in item]
        else:
            return None
    
    for onef in newfiles:
        fp = ana_dir + onef
        if "uFEMB" in onef :
            pos = onef.find("uFEMB")
            ufemb_id = int(onef[pos+5])
            dates = onef[7:15] 
            dr_fp= rst_dir + "uFEMB%d_%s_darkrate.hdf5"%(ufemb_id, dates)
            tg_fp= rst_dir + "uFEMB%d_%s_trigger.hdf5"%(ufemb_id, dates)
            create_structured_hdf5(hdf5_fp=dr_fp)
            create_structured_hdf5(hdf5_fp=tg_fp)


        if (".ana" in onef) or (".tana" in onef): 
            if (".ana" in onef) :
                hdf5_fp = dr_fp
            elif (".tana" in onef): 
                hdf5_fp = tg_fp
    
            if filter_anaed_file(hdf5_fp=hdf5_fp, anafp=onef  ):
                #used_files.append(onef)
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


rootdir = """G:/SiPM/"""


if True:
    for root, dirs, files in os.walk(rootdir):
        break

    subdirs = []
    dates = datetime.now().strftime("%Y%m%d")

    if True:
        yorn = input ("LED cali? (Y/N) (e/E exit): " )
        if "y" in yorn or "Y" in yorn:
            print ("One minute quick LED calibration start ...")
            import sg_control
            time.sleep(120)
            print ("One minute quick LED calibration End ...")
        elif "e" in yorn or "E" in yorn:
            exit()

        for rawd in dirs:
            if ("Rawdata_" in rawd) and (dates in rawd) :
                STEP2(rootdir, subdir=rawd)
                cur_dir = rawd
        from hdf5_trig_plot_step3 import hdf5_trig_plot_step3
        hdf5_trig_plot_step3 ()
        print ("""Done, please re-run 'C:/Users\protoDUNE/anaconda3/python.exe data_2_hdf5_step2.py'""")


    
