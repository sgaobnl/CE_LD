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

crateno = int(input("Crate no(1-6): "))
PTBslotno = int(input("PTB slot no(1-6): "))

#for PTBslotno in range(1,7):
#for PTBslotno in [6]:
while (crateno < 5) and (crateno > 0):
    while (PTBslotno < 7) and (PTBslotno > 0):
        a = FEMB_QC()
#        a.userdir = "/home/nfs/sgao/SBND_Installation/data/"
#        a.user_f = a.userdir + "tmp.csv"
#        a.databkdir = "/home/nfs/sgao/SBND_Installation/data/0622/noise_a_short/"
#        a.f_qcindex = a.databkdir + "tmp.csv"
        a.userdir = "/Users/shanshangao/Documents/SBND/0622/"
        a.user_f = a.userdir + "tmp.csv"
        a.databkdir = "/Users/shanshangao/Documents/SBND/0622/chk_post_bolt/"
        a.f_qcindex = a.databkdir + "tmp.csv"
     
        a.env = "RT"
        a.CLS.WIB_ver = 0x122
        FEMB_infos = a.FEMB_CHKOUT_Input(crateno, PTBslotno)
    
        a.WIB_IPs = ["10.226.34." + str( ((crateno-1)%4)*6 + PTBslotno) ]
        print (a.WIB_IPs)
        a.CLS.WIB_IPs = a.WIB_IPs

        a.CLS.pwr_femb_ignore = True
        if False:
            a.CLS.WIBs_SCAN()
            a.CLS.FEMBs_SCAN()
            a.CLS.FEMBs_CE_OFF()
        else:
            #a.FEMB_QC_PWR( FEMB_infos, pwr_int_f = False)
            a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 1 , ana_flg=True )
            #a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 6 , ana_flg=True)
            #a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 5 , ana_flg=True )
            #a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 5 )
    
    
        PTBslotno = int(input("PTB slot no(1-6): "))
    crateno = int(input("Crate no(1-6): "))
    if (crateno < 5) and (crateno > 0):
        PTBslotno = int(input("PTB slot no(1-6): "))
print ("Well Done")


