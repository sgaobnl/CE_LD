# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/1/2019 5:45:35 PM
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
import codecs
from cls_config import CLS_CONFIG

class FM_QC:
    def __init__(self):
        self.f_fm_qcindex = "./FM_QCindex.csv"
        self.fm_qclist = []
        self.WIB_IPs = ["192.168.121.1"]
        self.pwr_n = 5
        self.CLS = CLS_CONFIG()
        self.CLS.WIB_IPs = self.WIB_IPs 
        self.CLS.FM_only_f = True
#        self.CLS.act_fembs = {"192.168.121.1": [True, True, True, True] }

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
        for i in range(4):
            while (True):
                FM_id = input("Please enter ID of FM in WIB slot%d (input \"OFF\" if no FM): "%i)
                cf = input("WIB slot%d with FM ID#%s, Y or N? "%(i, FM_id) )
                if (cf == "Y"):
                    break
            if FM_id in FMlist:
                print ("FM ID#%s has been tested before, please input a short note for this retest\n"%FM_id)
                c_ret = input("Reason for retest: ")
                for fm_i in range(len(self.fm_qclist)):
                    if self.fm_qclist[i][1] == FM_id :
                        self.fm_qclist[i].append(c_ret)
            FM_ids.append("SLOT%d_"%i + FM_id)
        return FM_ids

    def FM_QC_ACQ(self):
        self.CLS.val = 10
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = True
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()
        # channel_mapping
        cfglog = self.CLS.CE_CHK_CFG(data_cs = 3)
        qc_data = self.CLS.TPC_UDPACQ(cfglog)
        self.CLS.FEMBs_CE_OFF()
        return qc_data

    def FM_QC_ANA(self, FM_ids, qc_data):
        for fm_id in FM_ids:
            femb_addr = int(fm_id[4])
            for femb_data in qc_data:
                if (femb_data[0][1] == femb_addr) :
                    fdata =  femb_data
                    sts_d = fdata[2][0]
                    data = fdata[1][0][0:100]
                    print (codecs.encode((data), 'hex') )
                    break

    def FM_STS_ANA(self, fm_id, sts_d):

a = FM_QC()
#FM_ids = a.FM_QC_Input()
FM_ids = ["SLOT0_OFF", "SLOT1_OFF", "SLOT2_OFF", "SLOT3_S1"]  
qc_data = a.FM_QC_ACQ()
a.FM_QC_ANA(FM_ids, qc_data)
