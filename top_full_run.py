# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Wed Mar 13 01:29:06 2024
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
#    elif ".14" in wib_ip:
#        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".26" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".36" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
    elif ".46" in wib_ip:
        LD.act_fembs[wib_ip] = [True, True, False, False]
#    elif ".34.34" in wib_ip:
#        LD.act_fembs[wib_ip] = [False, True, True, True]
    else:
        LD.act_fembs[wib_ip] = [True, True, True, True]

def Create_Folder():
    runtime =  datetime.now().strftime('%Y_%m_%d_%H_%M_%S') 
    print ("Test starts ", runtime)
    savedir ="""/scratch_local/SBND_Installation/data/commissioning/full_run/""" 
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

def DAQ(cfglog):
    time.sleep(2)
    cfgfn = LD.savedir + "CE.CFG"
    with open(cfgfn, "wb") as fp:
        pickle.dump(cfglog, fp)
    LD.TPC_UDPACQ(cfglog)


print ("############################################################################################")
print ("BL 200mv vs 900mV")
#14mV/fC, 2.0us, 200mV, RMS 
Create_Folder()
cfglog = CLS.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=1)
DAQ(cfglog)

#14mV/fC, 2.0us, 900mV, RMS 
Create_Folder()
cfglog = CLS.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=0)
DAQ(cfglog)

print ("Different Tps")
#14mV/fC, 900mV, RMS 
for i in range(4):
    st0 = i%2
    st1 = i//2
    Create_Folder()
    cfglog = CLS.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =st0, st1=st1, snc=0)
    DAQ(cfglog)

print ("Different gains")
#2.0us, 900mV, RMS 
for i in range(4):
    sg0 = i%2
    sg1 = i//2
    Create_Folder()
    cfglog = CLS.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=sg0, sg1=sg1, st0 =1, st1=1, snc=0)
    DAQ(cfglog)

print ("Different Leak Currents")
#14, 2.0us, 900mV, RMS 
for i in range(4):
    slk0 = i%2
    slk1 = i//2
    Create_Folder()
    cfglog = CLS.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=0, slk0=slk0, slk1=slk1)
    DAQ(cfglog)

print ("FPGA-DAC") #20min
#14mV/fC, 2.0us, 200mV, FPGA_DAC
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
for dacv in range(64):
    CLS.CE_FPGADAC(fpgadac_v=dacv)
    Create_Folder()
    DAQ(cfglog)

print ("FPGA-DAC-DLY-RUN")
#14mV/fC, 2.0us, 200mV, FPGA_DAC 
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
for dly in range(50):
    CLS.CE_PLSDLY(dly=dly)
    Create_Folder()
    DAQ(cfglog)

#7.8mV/fC, 2.0us, 200mV, FPGA_DAC 
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
for dacv in range(0,64,4):
    CLS.CE_FPGADAC(fpgadac_v=dacv)
    Create_Folder()
    DAQ(cfglog)

#14mV/fC, 2.0us, 900mV, FPGA_DAC
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=0, swdac1=1, swdac2=0, data_cs=0)
for dacv in range(0,32,4):
    CLS.CE_FPGADAC(fpgadac_v=dacv)
    Create_Folder()
    DAQ(cfglog)

#7.8mV/fC, 2.0us, 900mV, FPGA_DAC 
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, snc=0, swdac1=1, swdac2=0, data_cs=0)
for dacv in range(0,64,4):
    CLS.CE_FPGADAC(fpgadac_v=dacv)
    Create_Folder()
    DAQ(cfglog)


#14mV/fC, 0.5us, 200mV, FPGA_DAC
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=0, snc=1, swdac1=1, swdac2=0, data_cs=0)
for dacv in range(0,32,4):
    CLS.CE_FPGADAC(fpgadac_v=dacv)
    Create_Folder()
    DAQ(cfglog)

#14mV/fC, 1.0us, 200mV, FPGA_DAC
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =0, st1=0, snc=1, swdac1=1, swdac2=0, data_cs=0)
for dacv in range(0,32,4):
    CLS.CE_FPGADAC(fpgadac_v=dacv)
    Create_Folder()
    DAQ(cfglog)

#14mV/fC, 2.0us, 200mV, FPGA_DAC
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
for dacv in range(0,32,4):
    CLS.CE_FPGADAC(fpgadac_v=dacv)
    Create_Folder()
    DAQ(cfglog)

#14mV/fC, 3.0us, 200mV, FPGA_DAC
cfglog = CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =0, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
for dacv in range(0,32,4):
    CLS.CE_FPGADAC(fpgadac_v=dacv)
    Create_Folder()
    DAQ(cfglog)

#14mV/fC, 2.0us, 200mV, ASIC_DAC
for dacv in range(0,63,4):
    CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, asicdac_en=1, sts=1, sg0=0, sg1=1, st0 =1, st1=1, swdac1=0, swdac2=1, dac= dacv, data_cs=0)
    Create_Folder()
    DAQ(cfglog)

print ("Done")

