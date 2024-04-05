# -*- coding: utf-8 -*-
"""
File Name: LD_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Fri Apr  5 12:29:51 2024
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
#from setdatadir import savedir

LD = CLS_CONFIG()
LD.val=200

LD.ldflg=True
LD.UDP.MultiPort = True
LD.WIB_IPs = [
#                      "10.226.34.11",
#                      "192.168.121.1",
        #              "10.226.34.12",
        #              "10.226.34.13",
        #              "10.226.34.14",
                      "10.226.34.15",
        #              "10.226.34.16", 
        #              "10.226.34.21",
        #              "10.226.34.22",
        #              "10.226.34.23",
        #              "10.226.34.24",
        #              "10.226.34.25",
        #              "10.226.34.26", 
        #              "10.226.34.31",
        #              "10.226.34.32",
        #              "10.226.34.33",
        #              "10.226.34.34",
        #              "10.226.34.35",
        #              "10.226.34.36",
        #              "10.226.34.41",
        #              "10.226.34.42",
        #              "10.226.34.43",
        #              "10.226.34.44",
        #              "10.226.34.45",
        #      "10.226.34.46"
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

savedir ="""/scratch_local/SBND_Installation/data/commissioning/mon_run/""" 
if (os.path.exists(LD.savedir)):
    print (savedir)

def Create_Folder():
    runtime =  datetime.now().strftime('%Y_%m_%d_%H_%M_%S') 
    print ("Test starts ", runtime)
    LD.savedir = savedir + "/LD_" + runtime + "/"
    if (os.path.exists(LD.savedir)):
        pass
    else:
        try:
            os.makedirs(LD.savedir)
        except OSError:
            print ("Error to create folder %s"%LD.savedir)
            sys.exit()
    print("Save data in "+LD.savedir)


if True:
    textnote = "{}:".format(datetime.now())
    textnote += "Analog Monitoring \n"
    Create_Folder()
    cfglog = LD.CE_MON_CFG(pls_cs=0, dac_sel=0, mon_cs=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=0, monchn=40)
    #cfglog = LD.CE_MON_CFG(pls_cs=1, dac_sel=1, mon_cs=1, asicdac_en=1, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=0, swdac1=0, swdac2=1, dac=0x20, monchn=40)
    #cfglog = LD.CE_MON_CFG(pls_cs=1, dac_sel=1, mon_cs=0, asicdac_en=1, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=0, swdac2=1, dac=0x10, monchn=10)
    #cfglog = LD.CE_MON_CFG(pls_cs=0, dac_sel=0, mon_cs=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=1, monchn=0)
#    cfglog = LD.CE_MON_CFG(pls_cs=1, dac_sel=1, mon_cs=1, asicdac_en=1, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=0, swdac2=1, dac=0x20, monchn=49)


print ("Done")

