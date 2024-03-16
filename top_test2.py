# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Wed Jan 31 21:29:19 2024
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

LD = CLS_CONFIG()
LD.val=200
LD.savedir = "/scratch_local/SBND_Installation/data/sgao_02012024/LD1/"
if (os.path.exists(LD.savedir)):
    pass
else:
    try:
        os.makedirs(LD.savedir)
    except OSError:
        print ("Error to create folder %s"%LD.savedir)
        sys.exit()

LD.ldflg=True
LD.WIB_IPs = [
              "10.226.34.11",
              "10.226.34.12",
              "10.226.34.13",
              "10.226.34.14",
              "10.226.34.15",
#              "10.226.34.16" #delete later
              "10.226.34.16", 
              "10.226.34.21",
              "10.226.34.22",
              "10.226.34.23",
              "10.226.34.24",
              "10.226.34.25",
              "10.226.34.26", 
              "10.226.34.31",
              "10.226.34.32",
              "10.226.34.33",
              "10.226.34.34",
              "10.226.34.35",
              "10.226.34.36",
              "10.226.34.41",
              "10.226.34.42",
              "10.226.34.43",
              "10.226.34.44",
              "10.226.34.45",
              "10.226.34.46"
              ]
for wib_ip in LD.WIB_IPs:
    print (wib_ip)
    if ".16" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
#    elif ".14" in wib_ip:
#        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".26" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".36" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".46" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".34.34" in wib_ip:
        LD.act_fembs[wib_ip] = [False, True, True, True]
    else:
        LD.act_fembs[wib_ip] = [True, True, True, True]

for wib_ip in LD.WIB_IPs:
    LD.UDP.UDP_IP = wib_ip
    LD.UDP.MultiPort = True
    val = LD.UDP.read_reg_wib(0xFF)
    #print (wib_ip, "WIB", hex(val))
    for fembno in range(4):
        if LD.act_fembs[wib_ip][fembno]:
            if fembno == 5:
                LD.UDP.write_reg_femb_checked(fembno, 0x2A, (fembno<<4)+0)
            else:
                LD.UDP.write_reg_femb_checked(fembno, 0x2A, (fembno<<4)+0)
            val = LD.UDP.read_reg_femb(fembno, 0x2A)
            print (wib_ip, fembno, hex(val))
            #if val >= 0:
            #    wrval = 3
            #    LD.UDP.write_reg_femb_checked(fembno, 0x2A, wrval)
#exit()
i = 1
while True:
    print ("Time#" , i)
    i = i + 1

    for wib_ip in LD.WIB_IPs:
        LD.UDP.UDP_IP = wib_ip
        val = LD.UDP.read_reg_wib(0xFF)
    #print (wib_ip, "WIB", hex(val))
        for fembno in range(4):
            if LD.act_fembs[wib_ip][fembno]:
                LD.UDP.write_reg_femb_checked(fembno, 0x2A, 0)
    print ("rawdata")
 
    flg = False
    for wib_ip in LD.WIB_IPs:
        LD.UDP.UDP_IP = wib_ip
        val = LD.UDP.read_reg_wib(43)
        if ("16" in wib_ip) and ((val&0xff) != 0):
            print ("rawdata, warning...", wib_ip, "WIB", hex(val))
            flg = True
        elif ("16" not in wib_ip) and ((val&0xffff) != 0):
            print ("rawdata, warning...", wib_ip, "WIB", hex(val))
            flg = True
        else:
            print ("rawdata, correct...", wib_ip, "WIB", hex(val))
    #############################################################3
    for wib_ip in LD.WIB_IPs:
        LD.UDP.UDP_IP = wib_ip
        val = LD.UDP.read_reg_wib(0xFF)
        for fembno in range(4):
            if LD.act_fembs[wib_ip][fembno]:
                LD.UDP.write_reg_femb_checked(fembno, 0x2A, (fembno<<4)+3)

#    for wib_ip in LD.WIB_IPs:
#        LD.UDP.UDP_IP = wib_ip
#        LD.UDP.write_reg_wib_checked(20, 0)
#    time.sleep(0.1)
#    for wib_ip in LD.WIB_IPs:
#        LD.UDP.UDP_IP = wib_ip
#        LD.UDP.write_reg_wib_checked(20, 2)
#    time.sleep(0.1)
#    for wib_ip in LD.WIB_IPs:
#        LD.UDP.UDP_IP = wib_ip
#        LD.UDP.write_reg_wib_checked(20, 0)
#    time.sleep(0.1)
#    print ("chn mapping")
# 
    flg = False
    for wib_ip in LD.WIB_IPs:
        LD.UDP.UDP_IP = wib_ip
        val = LD.UDP.read_reg_wib(43)
        if (("16" in wib_ip) or ("26" in wib_ip) or ("36" in wib_ip) or ("46" in wib_ip) ) and ((val&0xff) != 0):
            print ("chn mapping error...", wib_ip, "WIB", hex(val))
            flg = True
        elif ("16" not in wib_ip) and ("26" not in wib_ip) and ("36" not in wib_ip) and ("46" not in wib_ip) and ((val&0xffff) != 0):
            print ("chn mapping error...", wib_ip, "WIB", hex(val))
            flg = True
        else:
            print ("chn mapping correct...", wib_ip, "WIB", hex(val))
    if flg:
        exit()
	

#for wib_ip in LD.WIB_IPs:
#    LD.UDP.UDP_IP = wib_ip
#    if mp == 1:
#        LD.UDP.UDP_PORT_RREGRESP = 32000 + 0x10 + int(wib_ip[-2:])
#        val = LD.UDP.read_reg_wib(0xFF)
#        print (hex(val))
#    elif mp == 0:
#        LD.UDP.UDP_PORT_RREGRESP = 32002
#        val = LD.UDP.read_reg_wib(0xFF)
#        print (hex(val))

print ("Done")

#cfglog = ""
#LD.TPC_UDPACQ(cfglog)

print ("Done")

