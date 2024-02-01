# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/28/2023 4:53:22 PM
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
from cls_config import CLS_CONFIG
from raw_convertor import RAW_CONV
import pickle
from shutil import copyfile
from femb_qc import FEMB_QC


cratenos = []
while True:
    for ci in [1,2,3,4]:
        onstr =  input("Choose crate#%d ON ? (Y/N): "%(ci))
        if "Y" in onstr or "y" in onstr:
            cratenos.append(ci)
    print (" FEMBs on crate  ", cratenos, "will be turned on") 
    ynstr = input ("Confirm? (Y/N")
    if "Y" in onstr or "y" in ynstr:
        break
    

for crateno in cratenos:
    PTBslotno = 1
    while (PTBslotno < 7) and (PTBslotno > 0):
        a = FEMB_QC()
        a.userdir = "/home/nfs/sgao/SBND_Installation/data/1129/OFF/"  
        #a.databkdir = "/home/nfs/sgao/SBND_Installation/data/1129/OFF/"
        a.databkdir = a.userdir 
        a.user_f = a.userdir + "tmp.csv"
        a.f_qcindex = a.databkdir + "tmp.csv"
        if (os.path.exists(a.userdir )):
            pass
        else:
            try:
                os.makedirs(a.userdir )
            except OSError:
                print ("Error to create folder %s"%a.userdir )
                sys.exit()
        if (os.path.exists(a.databkdir )):
            pass
        else:
            try:
                os.makedirs(a.databkdir )
            except OSError:
                print ("Error to create folder %s"%a.databkdir )
                sys.exit()
      
        a.env = "RT"
        a.CLS.WIB_ver = 0x123
        FEMB_infos = a.FEMB_CHKOUT_Input(crateno, PTBslotno)
    
        a.WIB_IPs = ["10.226.34." + str( crateno*10 + PTBslotno) ]
        print (a.WIB_IPs)
        a.CLS.WIB_IPs = a.WIB_IPs

        a.CLS.pwr_femb_ignore = False
        if True:
            a.CLS.WIBs_SCAN()
 #           a.CLS.FEMBs_SCAN()
            a.CLS.FEMBs_CE_OFF_DIR(wib_ip=a.WIB_IPs[0])
        PTBslotno = PTBslotno +1 #int(input("PTB slot no(1-6): "))
    #crateno = int(input("Crate no(1-6): "))
    #crateno = crateno + 1
#    if (crateno < 5) and (crateno > 0):
#        PTBslotno = int(input("PTB slot no(1-6): "))
print ("Well Done")


