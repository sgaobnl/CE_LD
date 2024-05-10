# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/10/2024 10:56:28 AM
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
from setdatadir import savedir


a = FEMB_QC()
crateno = 1
PTBslotno = 1
#a.env = "RT"
fembno_str = input("FEMB No:")
a.env = input("RT or LN:")

while True:
    try :
        fembslotno = int(input("FEMB on WIB Slot# (1-4) :"))
        if (1<= fembslotno) and (fembslotno <=4):
            a.CLS.femb_sws[fembslotno-1] = 1
            break
    except OSError:
        print ("Please input a number between 1 to 4 according to which WIB slot is attached with a FEMB")

print ("Please choose the operation mode list below:")
print ("Mode 0: Turn FEMB off")
print ("Mode 1: Turn FEMB on")
print ("Mode 2: Configure FEMB for normal operation")
print ("Mode 3: Configure FEMB into checkout operation")
print ("Mode 4: Local diagnostics mode (no configuration, just data taking)")
while True:
    try :
        modeno = int(input("FEMB on WIB Slot# (0-4) :"))
        if (0<= modeno) and (modeno <=4):
            break
    except OSError:
        print ("Please input a number between 0 to 4 according to which WIB slot is attached with a FEMB")

a.userdir = savedir + "/FEMB_" + fembno_str + "_" + a.env + "/Mode%02d/"%modeno
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

a.CLS.WIB_ver = 0x120
FEMB_infos = a.FEMB_CHKOUT_Input(crateno, PTBslotno)
a.WIB_IPs = ["192.168.121.1" ]
a.CLS.UDP.MultiPort = False
a.CLS.WIB_IPs = a.WIB_IPs
a.CLS.val = 200 #data amount to take

if modeno == 0:
    for wib_ip in a.WIB_IPs:
        a.CLS.FEMBs_CE_OFF_DIR(wib_ip )
elif modeno == 1:
    a.CLS.pwr_femb_ignore = False
    a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 1, ana_flg=True )
elif modeno == 2:
    a.CLS.pwr_femb_ignore = True
    a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 5, ana_flg=True )
elif modeno == 3:
    a.CLS.pwr_femb_ignore = True
    a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 4, ana_flg=True )
elif modeno == 4:
    a.CLS.pwr_femb_ignore = True
    a.CLS.ldflg=True
    for wib_ip in a.WIB_IPs:
        a.CLS.act_fembs[wib_ip] = [False, False, False, False]
        for i in range(4):
            if a.CLS.femb_sws[i] == 1:
                a.CLS.act_fembs[wib_ip][i] = True
            else:
                a.CLS.act_fembs[wib_ip][i] = False
        cfglog = ""
        runtime =  datetime.now().strftime('%Y_%m_%d_%H_%M_%S') 
        a.CLS.savedir = a.userdir  + "/LD_" + runtime + "/"
        if (os.path.exists(a.CLS.savedir)):
            ynstr = input ("Path exist, continue? (Y/N) " )
            if "Y" in ynstr or "y" in ynstr:
                pass
            else:
                exit()
        else:
            try:
                os.makedirs(a.CLS.savedir)
            except OSError:
                print ("Error to create folder %s"%a.CLS.savedir)
                sys.exit()
        a.CLS.TPC_UDPACQ(cfglog)
elif modeno == 4:
    monchnno = int(input("input a channel number (0-127) for monitoring>> "))
    a.CLS.CE_MON_CFG(pls_cs=0, dac_sel=0, mon_cs=1, sts=0, sg0=0, sg1=0, st0 =1, st1=1, snc=0, monchn=monchnno)


print ("Data save at :", a.userdir)
print ("Well Done")


