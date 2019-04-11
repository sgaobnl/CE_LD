# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/11/2019 5:31:34 PM
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
import pickle
from shutil import copyfile

class FM_QC:
    def __init__(self):
        self.jumbo_flag = False
        self.userdir = "I:/SBND_QC/"
        self.user_fm_f = self.userdir + "FM_QCindex.csv"
        self.databkdir = "I:/SBND_QC/FM_QC/"
        self.f_fm_qcindex = self.databkdir + "FM_QCindex.csv"
        self.fm_qclist = []
        self.WIB_IPs = ["192.168.121.1"]
        self.pwr_n = 5
        self.CLS = CLS_CONFIG()
        self.CLS.WIB_IPs = self.WIB_IPs 
        self.CLS.FEMB_ver = 0x501
        self.CLS.FM_only_f = True
        self.CLS.jumbo_flag = self.jumbo_flag 
        self.RAW_C = RAW_CONV()
        self.RAW_C.jumbo_flag = self.jumbo_flag 
        self.raw_data = []

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
                    self.fm_qclist.append(x)
        fm_ids = []
        for fm in self.fm_qclist:
            fm_ids.append(fm[2])
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
                print ("FM ID#%s has been tested before, please input a short note for this rerun"%FM_id)
                c_ret = input("Reason for retest: ")
                rerun_f = "Y"
            else:
                c_ret = ""
                rerun_f = "N"
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

    def FM_QC_ANA(self, FM_infos, qc_data, pwr_i = 0):
        qcs = []
        for fm_info in FM_infos:
            fms = fm_info.split("\n")
            femb_addr = int(fms[0][4])
            fm_id = fms[1]
            fm_env = fms[2]
            fm_rerun_f = fms[3]
            fm_c_ret = fms[4]
            fm_date = self.CLS.err_code[self.CLS.err_code.index("#TIME") +5: self.CLS.err_code.index("#IP")] 
            errs = self.CLS.err_code.split("SLOT")
            for er in errs[1:]:
                if( int(er[0]) == femb_addr ):
                    if (len(er) <2 ):
                        fm_errlog = ""
                    else:
                        fm_errlog = er[2: er.index("#IP")] if "#IP" in er else er[2: ]
                    break

            if  "OFF" in fm_id:
                pass
            else :
                qc_list = ["FAIL", fm_env, fm_id, fm_rerun_f, fm_date, fm_errlog, fm_c_ret, "PWR%d"%(pwr_i+1)] 
                map_r = None
                sts = None
                for femb_data in qc_data:
                    if (femb_data[0][1] == femb_addr): 
                        fdata =  femb_data
                        sts_r = fdata[2][0]
                        fmdata = fdata[1]
                        map_r = self.FM_MAP_CHK(femb_addr, fmdata)
                        sts = fdata[2]

                        if (len(fm_errlog) == 0):
                            if map_r[0] : 
                                qc_list[0] = "PASS" 
                            else:
                                qc_list[0] = "FAIL" 
                                qc_list[-3] += map_r[1]
                        break
                qcs.append(qc_list )
                self.raw_data.append([qc_list, map_r, sts])

        return qcs

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


    def FM_QC_PWR(self, FM_infos):
        pwr_qcs = []
        for pwr_i in range(self.pwr_n ):
            print ("Power Cycle %d of %d starts..."%(pwr_i, self.pwr_n))
            qc_data = self.FM_QC_ACQ()
            qcs = self.FM_QC_ANA(FM_infos, qc_data, pwr_i)
            pwr_qcs += qcs
            print ("Power Cycle %d of %d is done, wait 30 seconds"%(pwr_i, self.pwr_n))
            time.sleep(30)

        saves = []
        for fm_info in FM_infos:
            fms = fm_info.split("\n")
            fm_id = fms[1]
            flg = False
            for qct in pwr_qcs:
                if qct[2] == fm_id :
                    if qct[0] == "PASS" :
                        pass_qct = qct
                        flg = True
                    else:
                        saves.append(qct)
                        flg = False
                        break
            if (flg):
                saves.append(pass_qct)

        with open (self.f_fm_qcindex , 'a') as fp:
            print ("Result,ENV,FM_ID,Retun Test,Date,Error_Code,Note,Powr Cycle,")
            for x in saves:
                fp.write(",".join(str(i) for i in x) +  "," + "\n")
                print (x)
        copyfile(self.f_fm_qcindex, self.user_fm_f )

        if (len(pwr_qcs) > 0 ):
            fn =self.databkdir  + "FM_QC_" + pwr_qcs[0][1] +"_" + pwr_qcs[0][4] + ".bin" 
            with open(fn, 'wb') as f:
                pickle.dump(self.raw_data, f)
        print ("Result is saved in %s"%self.user_fm_f )
        print ("Well Done")


a = FM_QC()
FM_infos = a.FM_QC_Input()
a.FM_QC_PWR( FM_infos)

