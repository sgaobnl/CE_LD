# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 9/12/2025 1:38:58 PM
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

rootp = "G:/SiPM/Anaata_20250629_00_00/"
fn = "uFEMB1_20250629_00_10_00000000000000000435430392047601.tana"    
#rootp = "G:/SiPM/Anaata_20250705_00_00/"
#fn = "uFEMB1_20250705_00_20_00000000000000000487328126713514.tana"    
#fn = "uFEMB1_20250609_00_08_00000000000000000262622153148651.ana"
fp = rootp + "/" + fn

fm = """D:/GitHub/CE_LD/chn_mapping.csv""" #femb1
#fm = """C:/uFEMB/CE_LD/chn_mapping.csv""" #femb2
#fm = """C:/Users/sgao.BNL/Documents/GitHub/CE_LD/chn_mapping.csv"""

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

tdszip = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
with open (fp, "rb") as fs:
    datas = pickle.load(fs)

    chi =int( input ("CH = (0-31) :")) 
    label = dmap[chi]
    if True:
        if len(datas[chi])> 0:
            import matplotlib.pyplot as plt

            for xi in range(len(datas[chi])):
                fig = plt.figure(figsize=(16,8))
                if xi == 0:
                    plt.plot((np.arange(len(datas[chi][xi][1])))*0.5, datas[chi][xi][1], marker = '*' , label=label)
                else:                                                                                
                    plt.plot((np.arange(len(datas[chi][xi][1])))*0.5, datas[chi][xi][1], marker = '*' )

            #plt.title('Total Triggers = %d'%(len(datas[chi])))
                plt.xlabel('Time / us')
                plt.ylabel('ADC / bit')
                plt.legend(loc=1,fontsize=10)
                plt.grid()
                plt.show()
                plt.close()




    
