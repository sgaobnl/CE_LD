# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Wed Apr 10 09:56:36 2024
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
LD.savedir = "/scratch_local/SBND_Installation/data/commissioning/ColdFPGA_TX_RST/"
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
    elif ".26" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".36" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".46" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    else:
        LD.act_fembs[wib_ip] = [True, True, True, True]

for wib_ip in LD.WIB_IPs:
    LD.UDP.UDP_IP = wib_ip
    LD.UDP.MultiPort = True
    stats = LD.WIB_STATUS(wib_ip)
    runtime =  datetime.now().strftime('%Y_%m_%d_%H_%M_%S') 
    femb_addr = 0
    fn = LD.savedir + "/" + "STAS_" + "WIB_" + wib_ip.replace(".","_") + "FEMB_" + str(femb_addr) +  "_Time" + runtime + ".sts"
    print (fn)
    with open(fn, "wb") as fp:
        pickle.dump(stats, fp)


    for femb_addr in range(4):
        wib_regs = []
        if femb_addr == 1:
            for addr in range(0, 0x2A+1,1):
                val = LD.UDP.read_reg_wib(addr)
                wib_regs.append((addr,val))
            for addr in range(0xFF, 0x102+1,1):
                val = LD.UDP.read_reg_wib(addr)
                wib_regs.append((addr,val))
            wibfn = fn[0:-4] + ".wib"
            with open(wibfn, "wb") as fp:
                pickle.dump(wib_regs, fp)
        femb_regs = []
        for addr in range(0, 0x2B+1,1):
            val = LD.UDP.read_reg_femb(femb_addr, addr)
            femb_regs.append((addr,val))
        for addr in range(0x100, 0x104+1,1):
            val = LD.UDP.read_reg_femb(femb_addr, addr)
            femb_regs.append((addr,val))
        for addr in range(0x200, 0x298+1,1):
            val = LD.UDP.read_reg_femb(femb_addr, addr)
            femb_regs.append((addr,val))
        for addr in range(0x300, 0x3FF+1,1):
            val = LD.UDP.read_reg_femb(femb_addr, addr)
            femb_regs.append((addr,val))
        fembfn = fn[0:-4] + ".femb"
        with open(fembfn, "wb") as fp:
            pickle.dump(femb_regs, fp)

    keys = list(stats.keys())
    for key in keys:
        if ("_CHK_ERR_LINK" in key) and (stats[key] != 0) :
            fembno = int(key[4])
            print ("WIB IP %s: Set to output fake data"%( wib_ip))
            #set the WIB output fake data (channel mapping)
            LD.UDP.write_reg_wib_checked(0x09, 0x20)

            print ("FEMB%d of WIB IP %s: Set to reset ColdFPGA transceiver PLL"%(fembno, wib_ip))
            LD.UDP.write_reg_femb_checked(fembno, 0x14,0x01f80001)
            time.sleep(1)
            LD.UDP.write_reg_femb_checked(fembno, 0x14,0x01f80000)
            time.sleep(1)
            #set the WIB output normal data
            print ("WIB IP %s: Set to output normal data"%( wib_ip))
            LD.UDP.write_reg_wib_checked(0x09, 0x0)

print ("Done")

