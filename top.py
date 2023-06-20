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


ce = FEMB_QC()

#crateno = int(input("Crate no(1-6): "))
#PTBslotno = int(input("PTB slot no(1-6): "))
#wib_ip = input( "WIB IP address: ")
ce.env = "RT"
ce.CLS.WIB_ver = 0x122
crateno = 1
PTBslotno = 1
#wib_ip = "192.168.121.1"
#wib_ip = "192.168.230.50"
wib_ip = "10.226.34.1"
#mbb_ip = "192.168.121.11"
#ce.CLS.MBB_IP = mbb_ip

if True:
    ce.WIB_IPs = [wib_ip]
    ce.CLS.WIB_IPs = ce.WIB_IPs
    ce.FEMB_CHK_ACQ(testcode=1)

#    FEMB_infos = ce.FEMB_CHKOUT_Input(crateno, PTBslotno)
#    ce.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 1 )
#    for wib_ip in ce.WIB_IPs:
#        ce.CLS.WIB_SYNC(wib_ip)
#
#    while True:
#        sync = input ("SYNC Nevis DAQ (Y/N)?: ")
#        if "Y" in sync or "y" in sync:
#            for wib_ip in ce.WIB_IPs:
#                ce.CLS.WIB_SYNC(wib_ip)
#        else:
#            qflg = input ("Quit (Y/N)?: ")
#            if "Y" in sync or "y" in qflg:
#                print ("Done, exit")
#                exit()
#
