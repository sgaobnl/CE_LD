# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/3/2019 2:21:19 PM
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
from raw_convertor import RAW_CONV

class FM_QC:
    def __init__(self):
        self.jumbo_flag = False
        self.f_fm_qcindex = "./FM_QCindex.csv"
        self.fm_qclist = []
        self.WIB_IPs = ["192.168.121.1"]
        self.pwr_n = 5
        self.CLS = CLS_CONFIG()
        self.CLS.WIB_IPs = self.WIB_IPs 
        self.CLS.FEMB_ver = 0x405
        self.CLS.FM_only_f = True
        self.CLS.jumbo_flag = self.jumbo_flag 
        self.RAW_C = RAW_CONV()
        self.RAW_C.jumbo_flag = self.jumbo_flag 

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
        FM_infos = []
        env = input("Test is performed at (RT or LN)? :")
        for i in range(4):
            while (True):
                FM_id = input("Please enter ID of FM in WIB slot%d (input \"OFF\" if no FM): "%i)
                cf = input("WIB slot%d with FM ID#%s, Y or N? "%(i, FM_id) )
                if (cf == "Y"):
                    break
            if FM_id in FMlist:
                print ("FM ID#%s has been tested before, please input a short note for this retest\n"%FM_id)
                c_ret = input("Reason for retest: ")
                rerun_f = "Y"
            else:
                c_ret = ""
                rerun_f = "N"

#                for fm_i in range(len(self.fm_qclist)):
#                    if self.fm_qclist[i][1] == FM_id :
#                        self.fm_qclist[i].append(c_ret)
            FM_infos.append("SLOT%d"%i + "\n" + FM_id + "\n" + env + "\n" + rerun_f + "\n" + c_ret )
        return FM_infos

    def FM_QC_ACQ(self):
        self.CLS.val = 10 
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = True
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()
        cfglog = self.CLS.CE_CHK_CFG(data_cs = 3)# channel_mapping data
        qc_data = self.CLS.TPC_UDPACQ(cfglog)
        self.CLS.FEMBs_CE_OFF()
        return qc_data

    def FM_QC_ANA(self, FM_infos, qc_data):
        for fm_info in FM_infos:
            fms = fm_info.split("\n")
            femb_addr = int(fms[0][4])
            fm_id = fms[1]
            fm_env = fms[2]
            fm_rerun_f = fms[3]
            fm_c_ret = fms[4]
            fm_date = self.CLS.err_code[self.CLS.err_code.index("#TIME") : self.CLS.err_code.index("#IP")] 
            errs = self.CLS.err_code.split("SLOT")
            for er in errs:
                if( int(er[0]) == femb_ddr ):
                    if (len(er) <2 ):
                        er = ""
                    else
                        fm_errlog = [2:] 
                    break

            if  "OFF" in fm_id:
                pass
            else
                for femb_data in qc_data:
                    if (femb_data[0][1] == femb_addr) 
                        fdata =  femb_data
                        sts_r = fdata[2][0]
                        fmdata = fdata[1]
                        map_r = self.FM_MAP_CHK(femb_addr, fmdata)
                        qc_r = "PASS" if mar_r[0] else "FAIL"
                        self.fm_qclist.append( ["", fm_env, fm_id, fm_return_f, qc_r, fm_date, fm_errlog, fm_c_ret] )
                        print (["", fm_env, fm_id, fm_return_f, qc_r, fm_date, fm_errlog, fm_c_ret] )
                        break
                    else
                        qc_r = "FAIL"
                        self.fm_qclist.append( ["", fm_env, fm_id, fm_return_f, qc_r, fm_date, fm_errlog, fm_c_ret] )
                        print (["", fm_env, fm_id, fm_return_f, qc_r, fm_date, fm_errlog, fm_c_ret] )

#        self.fm_qclist.append( "")

    def FM_MAP_CHK(self, femb_addr, fmdata):
        chn_rb = []
        for adata in fmdata:
            atmp = self.RAW_C.raw_conv(adata)
            for chndata in atmp:
                chn_rb.append(chndata[0])
        wib_pos = femb_addr<<8
        for chn in range(128):
            if (wib_pos + chn) != (chn_rb[chn]&0x0FFF):
                err_code = "-F5_MAP_ERR"
                return (False, err_code, chn_rb)
        return (True, "-PASS", chn_rb)


 #   def FM_STS_ANA(self, fm_id, sts_d):

a = FM_QC()
##FM_ids = a.FM_QC_Input()
#FM_ids = ["SLOT0_OFF", "SLOT1_OFF", "SLOT2_OFF", "SLOT3_S1"]  
qc_data = a.FM_QC_ACQ()
#print (self.CLS.err_code)
#a.FM_QC_ANA(FM_ids, qc_data)


#apath = "./a.bin"
#import pickle
#with open(apath, 'rb') as f:
#    fmdata = pickle.load(f)
#print (a.FM_MAP_CHK(3, fmdata))
#data = a.RAW_C.raw_conv(data)
#print (data[0][0:10])
#print (len(data[0]))
#


#print (len(fmdata))
#apath = "./a.bin"
#import pickle
#with open(apath, 'wb') as f:
#    pickle.dump(fmdata, f)

