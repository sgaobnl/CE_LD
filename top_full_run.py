# -*- coding: utf-8 -*-
"""
File Name: LD_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 3/14/2024 7:27:00 AM
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
#LD.UDP.MultiPort = False
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
#LD.WIB_IPs = ["192.168.121.1"]
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

#LD.act_fembs[wib_ip] = [True, False, False, False]
savedir ="""/scratch_local/SBND_Installation/data/commissioning/full_run/""" 
print (savedir)
#savedir ="""D:/full_run/""" 

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

def DAQ(cfglog):
#    time.sleep(2)
    cfgfn = LD.savedir + "CE.CFG"
    with open(cfgfn, "wb") as fp:
        pickle.dump(cfglog, fp)
    LD.TPC_UDPACQ(cfglog)


recfn = savedir + "record.txt"

testno = int(sys.argv[1])
print ("############################################################################################")
if testno == 1:
    textnote = "{}:".format(datetime.now())
    textnote += "BL 200mv vs 900mV \n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)
    #14mV/fC, 2.0us, 200mV, RMS 
    #print ( datetime.now() )
    Create_Folder()
    #print ( datetime.now() )
    cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=1)
    #print ( datetime.now() )
    DAQ(cfglog)
    #print ( datetime.now() )

    #14mV/fC, 2.0us, 900mV, RMS 
    Create_Folder()
    cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=0)
    DAQ(cfglog)
    
if testno == 2:
    textnote = "{}:".format(datetime.now())
    textnote += "Different Tps\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    #14mV/fC, 900mV, RMS 
    for i in range(4):
        st0 = i%2
        st1 = i//2
        Create_Folder()
        cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =st0, st1=st1, snc=0)
        DAQ(cfglog)
    
if testno == 3:
    textnote = "{}:".format(datetime.now())
    textnote += "Different gains\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    #2.0us, 900mV, RMS 
    for i in range(4):
        sg0 = i%2
        sg1 = i//2
        Create_Folder()
        cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=sg0, sg1=sg1, st0 =1, st1=1, snc=0)
        DAQ(cfglog)
    
if testno == 4:
    textnote = "{}:".format(datetime.now())
    textnote += "Different Leak Currents: #14, 2.0us, 900mV, RMS\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    for i in range(4):
        slk0 = i%2
        slk1 = i//2
        Create_Folder()
        cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=0, slk0=slk0, slk1=slk1)
        DAQ(cfglog)
    
if testno == 5:
    textnote = "{}:".format(datetime.now())
    textnote += "FPGA-DAC: #14mV/fC, 2.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(32):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 6:
    textnote = "{}:".format(datetime.now())
    textnote += "FPGA-DAC-DLY-RUN:#14mV/fC, 2.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)
     
    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dly in range(50):
        LD.CE_PLSDLY(dly=dly)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 7:
    textnote = "{}:".format(datetime.now())
    textnote += " #7.8mV/fC, 2.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,64,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 8:
    textnote = "{}:".format(datetime.now())
    textnote += "#14mV/fC, 2.0us, 900mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=0, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,32,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 9:
    textnote = "{}:".format(datetime.now())
    textnote += "#7.8mV/fC, 2.0us, 900mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, snc=0, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,64,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 10:
    textnote = "{}:".format(datetime.now())
    textnote += "0.5us: #14mV/fC, 0.5us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=0, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,32,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 11:
    textnote = "{}:".format(datetime.now())
    textnote += "1.0us: #14mV/fC, 1.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =0, st1=0, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,32,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 12:
    textnote = "{}:".format(datetime.now())
    textnote += "2.0us: #14mV/fC, 2.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,32,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 13:
    textnote = "{}:".format(datetime.now())
    textnote += "3.0us TP: #14mV/fC, 3.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)
    
    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =0, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,32,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 14:
    textnote = "{}:".format(datetime.now())
    textnote += "ASIC-DAC: #14mV/fC, 2.0us, 200mV, ASIC_DAC\n"
    
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    for dacv in range(0,63,4):
        cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, asicdac_en=1, sts=1, sg0=0, sg1=1, st0 =1, st1=1, swdac1=0, swdac2=1, dac= dacv, data_cs=0)
        Create_Folder()
        DAQ(cfglog)

if testno == 15:
    textnote = "{}:".format(datetime.now())
    textnote += "FPGA-DAC (Saturation): #14mV/fC, 2.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(32,64,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
    
if testno == 16:
    textnote = "{}:".format(datetime.now())
    textnote += "FPGA-DAC: #7.8mV/fC, 2.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=0, sg0=1, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(32):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)

if testno == 17:
    textnote = "{}:".format(datetime.now())
    textnote += "Different gains @200mV\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    #2.0us, 200mV, RMS 
    for i in range(4):
        sg0 = i%2
        sg1 = i//2
        Create_Folder()
        cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=sg0, sg1=sg1, st0 =1, st1=1, snc=1)
        DAQ(cfglog)

if testno == 18:
    textnote = "{}:".format(datetime.now())
    textnote += " #4.7mV/fC, 2.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=0, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,64,4):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
 
if testno == 19:
    textnote = "{}:".format(datetime.now())
    textnote += " #25mV/fC, 2.0us, 200mV, FPGA_DAC\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=0, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
    for dacv in range(0,16,2):
        LD.CE_FPGADAC(fpgadac_v=dacv)
        Create_Folder()
        DAQ(cfglog)
 
if testno == 20:
    textnote = "{}:".format(datetime.now())
    textnote += "Different Tps 200mV\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    #14mV/fC, 200mV, RMS 
    for i in range(4):
        st0 = i%2
        st1 = i//2
        Create_Folder()
        cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =st0, st1=st1, snc=1)
        DAQ(cfglog)
    
if testno == 21:
    textnote = "{}:".format(datetime.now())
    textnote += "Different gains, 200mV\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    #2.0us, 200mV, RMS 
    for i in range(4):
        sg0 = i%2
        sg1 = i//2
        Create_Folder()
        cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=sg0, sg1=sg1, st0 =1, st1=1, snc=1)
        DAQ(cfglog)
    
if testno == 22:
    textnote = "{}:".format(datetime.now())
    textnote += "Different Leak Currents: #14, 2.0us, 200mV, RMS\n"
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    for i in range(4):
        slk0 = i%2
        slk1 = i//2
        Create_Folder()
        cfglog = LD.CE_CHK_CFG(pls_cs=0, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=1, slk0=slk0, slk1=slk1)
        DAQ(cfglog)

if testno == 23:
    textnote = "{}:".format(datetime.now())
    textnote += "ASIC-DAC: #14mV/fC, 2.0us, 200mV, ASIC_DAC\n"
    
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    for dacv in range(0,32,2):
        cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, asicdac_en=1, sts=1, sg0=0, sg1=1, st0 =1, st1=1, swdac1=0, swdac2=1, dac= dacv, data_cs=0)
        Create_Folder()
        DAQ(cfglog)

if testno == 24:
    textnote = "{}:".format(datetime.now())
    textnote += "ASIC-DAC: #7.8mV/fC, 2.0us, 200mV, ASIC_DAC\n"
    
    with open(recfn, "a+") as rfp:
        rfp.write(textnote)
    print (textnote)

    for dacv in range(0,64,8):
        cfglog = LD.CE_CHK_CFG(pls_cs=1, dac_sel=1, asicdac_en=1, sts=1, sg0=1, sg1=0, st0 =1, st1=1, swdac1=0, swdac2=1, dac= dacv, data_cs=0)
        Create_Folder()
        DAQ(cfglog)


print ("Done")

