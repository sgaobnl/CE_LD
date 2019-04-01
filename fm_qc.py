# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Mon Apr  1 10:54:29 2019
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
import numpy as np
#import scipy as sp
#import pylab as pl

import sys 
import string
import time
from datetime import datetime
import struct
from cls_config import CLS_CONFIG

class FM_QC:
    def __init__(self):
        self.f_fm_qcindex = "./FM_QCindex.csv"
        self.fm_qclist = []
        CLS = CLS_CONFIG()
        self.WIB_IPs = ["192.168.121.1"]
        CLS.WIB_IPs = self.WIB_IPs 
        self.pwr_n = 5

    def FM_INDEX_LOAD(self):
        self.fm_qclist = []
        with open(self.f_fm_qcindex, 'r') as fp:
            for cl in fp:
                tmp = cl.split(',')
                x = []
                for i in tmp:
                    x.append(i.replace(" ", ""))
                x = x[:-1]
                if (x[0][0] != "#"):
                    self.fm_qclist.append(x[1:])
        fm_ids = []
        for fm in self.fm_qclist:
            fm_ids.append(fm[1])
        return fm_ids

    def FM_QC_Input(self):
        FMlist = self.FM_INDEX_LOAD()
        FM_ids = []
        for i in range(4)
            while (True):
                FM_id = raw_input("Please enter ID of FM in WIB slot%d (input \"OFF\" if no FM): "%i)
                cf = raw_input("WIB slot%d with FM ID#%s, Y or N? "%(i, FM_id) )
                if (cf == "Y"):
                    break
            if FM_id in FMlist:
                print ("FM ID#%s has been tested before, please input a short note for this retest\n"%FM_id)
                c_ret = raw_input("Reason for retest: ")
                for fm_i in range(len(self.fm_qclist)):
                    if self.fm_qclist[i][1] == FM_id :
                        self.fm_qclist[i].append(c_ret)
            if ("OFF" in FE_id):
                FM_ids.append([0, FM_id])
            else:
                FM_ids.append([1, FM_id])
        return FM_ids

    def FM_QC_ACQ(self):
        CLS.val = 10
        CLS.sts_num = 3
        CLS.f_save = False
        CLS.WIBs_SCAN()
        CLS.FEMBs_SCAN()
        CLS.WIBs_CFG_INIT()
        # channel_mapping
        cfglog = CLS.CE_CHK_CFG(data_cs = 3)
        qc_data = CLS.TPC_UDPACQ(cfglog)
        CLS.FEMBs_CE_OFF()
        return qc_data

    def FM_STATUS(self, qc_data):


    def FM_QC_ANA(self, FM_ids, qc_data):
        for fm_id in FM_ids:
            if (fm_id[0] == 1):
                femb_addr = FM_ids(fm_id)
                for femb_data in tpc_data:
                    if (femb_data[1] == femb_addr) :
                        fdata =  femb_data
                        break
            #power & link checkout
            if fdata[2] == True:
                f_pass = True
            else:

#Power & LINK checkout
#        perr =         for pe in perr:
#            if len(pe[2]) == False:
#Power Cycle test
#        for pn in range(self.pwr_n) : 
#            print ("%d Power Cycle Test, please wait"%(pn+1))
#            time.sleep(30)



