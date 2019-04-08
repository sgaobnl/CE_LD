# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Mon Apr  8 15:20:04 2019
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

from FM_QC import FM_QC()

class FEMB_QC:
    def __init__(self):
        self.jumbo_flag = False
        self.datadir = "D:/SBND_QC/"
        self.f_femb_qcindex = self.datadir + "FEMB_QCindex.csv"
        self.femb_qclist = []
        self.WIB_IPs = ["192.168.121.1"]
        self.pwr_n = 5
        self.FMQC = FM_QC()
        self.FMQC.jumbo_flag = self.jumbo_flag 
        self.FMQC.CLS.FM_only_f = True

#        self.CLS.FEMB_ver = 0x405
#        self.RAW_C = RAW_CONV()
#        self.RAW_C.jumbo_flag = self.jumbo_flag 
#        self.raw_data = []

    def FEMB_INDEX_LOAD(self):
        self.femb_qclist = []
        with open(self.f_femb_qcindex, 'r') as fp:
            for cl in fp:
                tmp = cl.split(',')
                x = []
                for i in tmp:
                    x.append(i.replace(" ", ""))
                x = x[:-1]
                if (x[0][0] != "#"):
                    self.femb_qclist.append(x[1:])
        femb_ids = []
        for femb in self.femb_qclist:
            femb_ids.append(fm[1])
        return femb_ids

    def FEMB_QC_Input(self):
        FEMBlist = self.FEMB_INDEX_LOAD()
        FEMB_infos = []
        env = input("Test is performed at (RT or LN)? :")
        for i in range(4):
            while (True):
                print ("Please enter ID of FEMB in WIB slot%d (input \"OFF\" if no FEMB): "%i)
                FEMB_id = input("Format: FM-AM (e.g. FC1-SAC1) >>")
                cf = input("WIB slot%d with FEMB ID is \"#%s\", Y or N? "%(i, FEMB_id) )
                if (cf == "Y"):
                    break
            if FEMB_id in FEMBlist:
                print ("FEMB \"%s\" has been tested before, please input a short note for this retest\n"%FEMB_id)
                c_ret = input("Reason for retest: ")
                rerun_f = "Y"
            else:
                c_ret = ""
                rerun_f = "N"
            FEMB_infos.append("SLOT%d"%i + "\n" + FEMB_id + "\n" + env + "\n" + rerun_f + "\n" + c_ret )
        return FEMB_infos

    def FEMB_CHK_ACQ(self):
        self.CLS.val = 100 
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = False
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()
        #14mV/fC, 2.0us, 900mV, FPGA_DAC enable = 0x08
        cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=0, fpgadac_en=1, fpgadac_v=0x08, sg0=0, sg1=1, st0 =1, st1=1, swdac1=1, swdac2=0, data_cs=0)
        qc_data = self.CLS.TPC_UDPACQ(cfglog)
        self.CLS.FEMBs_CE_OFF()
        return qc_data

    def FEMB_CHK_ANA(self, FEMB_infos, qc_data, pwr_i = 0):
        qcs = []
        for femb_info in FEMB_infos:
            fms = femb_info.split("\n")
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
                        fm_errlog = er[2: er.index("#IP")]
                    break

            if  "OFF" in fm_id:
                pass
            else :
                qc_list = ["FAIL", fm_env, fm_id, fm_rerun_f, fm_date, fm_errlog, fm_c_ret, "PWR%d"%pwr_i] 
                for femb_data in qc_data:
                    if (femb_data[0][1] == femb_addr): 
                        fdata =  femb_data
                        sts_r = fdata[2][0]
                        fembdata = fdata[1]
                        map_r = self.FEMB_CHK(femb_addr, fembdata)


                        sts = fdata[2]
                        if (len(fm_errlog) == 0):
                            if map_r[0] : 
                                qc_list[0] = "PASS" 
                            else:
                                qc_list[0] = "FAIL" 
                                qc_list[-3] += map_r[1]
                        qcs.append(qc_list )
                        self.raw_data.append([qc_list, map_r, sts])
                        break
        return qcs

    def FEMB_CHK(self, femb_addr, fembdata):
        for adata in fembdata:
            chn_rmss = []
            chn_peds = []
            chn_pkps = []
            chn_pkns = []
            chn_data, feed_loc, chn_peakp, chn_peakn = self.RAW_C.raw_conv_peak(adata)
            for achn in range(len(chn_data)):
                for af in range(len(feed_loc[0:-2])):
                    achn_ped += chn_data[achn][leed_loc[af]+100: leed_loc[af+1] ] 
                arms = np.rms(achn_ped)
                aped = int(np.mean(achn_ped))
                apeakp = int(np.mean(chn_peakp[achn]))
                apeakn = int(np.mean(chn_peakn[achn]))
                chn_rmss.append(arms)
                chn_peds.append(aped)
                chn_pkps.append(apeakp)
                chn_pkns.append(apeakn)



        chn_rb = []
            for chndata in atmp:
                chn_rb.append(chndata[0])
        wib_pos = femb_addr<<8
        for chn in range(128):
            if (wib_pos + chn) != (chn_rb[chn]&0x0FFF):
                err_code = "-F5_MAP_ERR"
                return (False, err_code, chn_rb)
        return (True, "-PASS", chn_rb)




    def FM_MAP_CHK(self, femb_addr, fmdata):
        for adata in fmdata:
            chn_data, feed_loc, chn_peakp, chn_peakn = self.RAW_C.raw_conv_peak(adata)
            for chn in range(len(feed_loc)):
                achn_ped = []
                for ai in range(len(feed_loc[0:-2])):
                    achn_ped += chn_data[chn][leed_loc[ai]+100: leed_loc[ai+1] ] 
                aped = np.mean(achn_ped)
                arms = np.rms(achn_ped)

        chn_rb = []
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
        for pwr_i in range(self.pwr_n )
            qc_data = self.FM_QC_ACQ()
            qcs = self.FM_QC_ANA(FM_infos, qc_data, pwr_i)
            pwr_qcs += qcs

        for fm_info in FM_infos:
            fms = fm_info.split("\n")
            fm_id = fms[1]
            flg = False
            for qct in pwr_qcs:
                if qct[2] == fm_id :
                    if qct[1] == "FAIL" :
                        self.fm_qclist.append(qct)
                        break
                    else:
                        pass_qct = qct
                        flg = True
            if (flg):
                self.fm_qclist.append(pass_qct)

        with open (self.f_fm_qcindex , 'a') as fp:
            print ("Result,ENV,FM_ID,Retun Test,Date,Error_Code,Note,Powr Cycle,")
            for x in self.fm_qclist:
                fp.write(",".join(str(i) for i in x) +  "," + "\n")
                print (x)

        if (len(self.fm_qclist) > 0 ):
            fn =self.datadir + "FM_QC/" + "FM_QC_" + self.fm_qclist[1] +"_" + self.fm_qclist[4] + ".bin" 
            with open(fn, 'wb') as f:
                pickle.dump(self.raw_data, f)


a = FM_QC()
FM_infos = a.FM_QC_Input()
a.FM_QC_PWR( FM_infos)



