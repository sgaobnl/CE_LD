# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 3/31/2019 6:34:12 PM
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
        CLS = CLS_CONFIG()
        self.WIB_IPs = ["192.168.121.1"]
        CLS.WIB_IPs = self.WIB_IPs 

    def FM_INDEX_LOAD():
        fm_list = []
        with open(self.f_fm_qcindex, 'r') as fp:
            for cl in fp:
                tmp = cl.split(',')
                x = []
                for i in tmp:
                    x.append(i.replace(" ", ""))
                x = x[:-1]
                print x
                if (x[0] == "#"):
                    fm_list.append(x[1:]


a = FM_QC()
a.FM_INDEX_LOAD()

#    def FM_QC_Input():
#        FM_ids = []
#        for i in range(4)
#            while (True):
#                FM_id = raw_input("Please enter ID of FM in WIB slot%d (input 0 if no FM): "%i)
#                cf = raw_input("WIB slot%d with FM ID#%s, Y or N? "%(i, FM_id) )
#                if (cf == "Y"):
#                    break
#            if FM_id in FMlist:
#                print ("FM ID#%s has been tested before, please input a short note for this retest\n"%FM_id)
#                c_ret = raw_input("Reason for retest: ")
#            FM_ids.append(FM_id)
#        
#        FM_ids = raw_input("Please enter ID of FM in WIB slot1:  ")
#
#    def FM_QC_ACQ():
#        CLS.val = 10
#        CLS.sts_num = 3
#        CLS.f_save = False
#
#        CLS.WIBs_SCAN()
#        CLS.FEMBs_SCAN()
#        CLS.WIBs_CFG_INIT()
#        # channel_mapping
#        cfglog = CLS.CE_CHK_CFG(data_cs = 3)
#        qc_data = CLS.TPC_UDPACQ(cfglog)
#        CLS.FEMBs_CE_OFF()

