# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/8/2019 4:28:07 PM
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


class FEMB_QC:
    def __init__(self):
        self.jumbo_flag = False
        self.datadir = "D:/SBND_QC/"
        self.f_femb_qcindex = self.datadir + "FEMB_QCindex.csv"
        self.femb_qclist = []
        self.WIB_IPs = ["192.168.121.1"]
        self.pwr_n = 5
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
            fembs = femb_info.split("\n")
            femb_addr = int(fembs[0][4])
            femb_id = fembs[1]
            femb_env = fembs[2]
            femb_rerun_f = fembs[3]
            femb_c_ret = fembs[4]
            femb_date = self.CLS.err_code[self.CLS.err_code.index("#TIME") +5: self.CLS.err_code.index("#IP")] 
            errs = self.CLS.err_code.split("SLOT")
            for er in errs[1:]:
                if( int(er[0]) == femb_addr ):
                    if (len(er) <2 ):
                        fm_errlog = ""
                    else:
                        fm_errlog = er[2: er.index("#IP")]
                    break

            if  "OFF" in femb_id:
                pass
            else :
                qc_list = ["FAIL", femb_env, femb_id, femb_rerun_f, femb_date, fm_errlog, femb_c_ret, "PWR%d"%pwr_i] 
                for femb_data in qc_data:
                    if (femb_data[0][1] == femb_addr): 
                        fdata =  femb_data
                        sts_r = fdata[2][0]
                        fembdata = fdata[1]
                        map_r = self.FEMB_CHK( femb_addr, fembdata)
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

    def FEMB_CHK(self,  femb_addr, fembdata):
        for adata in fembdata:
            chn_rmss = []
            chn_peds = []
            chn_pkps = []
            chn_pkns = []
            chn_waves = []
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
                chn_pkps.append(apeakp-aped)
                chn_pkns.append(apeakn-aped)
                chn_waves.append( chn_data[achn][leed_loc[0]: leed_loc[1]] )
        ana_err_code = ""
        rms_mean = np.mean(chn_rmss)
        rms_thr = 5*np.std(chn_rmss) if 5*(np.std(chn_rmss) < 0.5*rms_mean) else 0.5*rms_mean
        for chn in range(128):
            if abs(chn_rmss(chn) - rms_mean) < rms_thr :
                pass
            else:
                ana_err_code += "-F9_RMS_CHN%d"%(chn)

        for gi in range(4): 
            ped_mean = np.mean(chn_peds[gi*32 : (gi+1)*32])
            pkp_mean = np.mean(chn_pkps[gi*32 : (gi+1)*32])
            pkn_mean = np.mean(chn_pkns[gi*32 : (gi+1)*32])
            ped_thr= 30 
            for chn in range(gi*32, (gi+1)*32, 1):
                if chn_pkps(chn) - chn_peds(chn) < 200:
                    ana_err_code += "-F9_NORESP_CHN%d"%(chn)
                if chn_peds(chn) - chn_pkns(chn) < 200:
                    ana_err_code += "-F9_NORESN_CHN%d"%(chn)
                if abs(chn_peds(chn) - ped_mean) > ped_thr :
                    ana_err_code += "-F9_PED_CHN%d"%(chn)
                if abs(1- chn_pkps(chn)/pkp_mean) > 0.2:
                    ana_err_code += "-F9_PEAKP_CHN%d"%(chn)
                if abs(1- chn_pkps(chn)/pkp_mean) > 0.2:
                    ana_err_code += "-F9_PEAKN_CHN%d"%(chn)
        if len(ana_err_code) > 0:
            return (False, ana_err_code, [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves])
        else:
            return (True, "-PASS", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves])

    def FEMB_QC_PWR(self, FEMB_infos):
        pwr_qcs = []
        for pwr_i in range(self.pwr_n )
            qc_data = self.FEMB_CHK_ACQ()
            qcs = self.FEMB_CHK_ANA(FEMB_infos, qc_data, pwr_i)
            pwr_qcs += qcs

        for femb_info in FEMB_infos:
            fembs = femb_info.split("\n")
            femb_id = fembs[1]
            flg = False
            for qct in pwr_qcs:
                if qct[2] == femb_id :
                    if qct[1] == "FAIL" :
                        self.femb_qclist.append(qct)
                        break
                    else:
                        pass_qct = qct
                        flg = True
            if (flg):
                self.femb_qclist.append(pass_qct)

        with open (self.f_femb_qcindex , 'a') as fp:
            print ("Result,ENV,FEMB_ID,Retun Test,Date,Error_Code,Note,Powr Cycle,")
            for x in self.femb_qclist:
                fp.write(",".join(str(i) for i in x) +  "," + "\n")
                print (x)

        if (len(self.femb_qclist) > 0 ):
            fn =self.datadir + "FEMB_QC/" + "FEMB_QC_" + self.femb_qclist[1] +"_" + self.femb_qclist[4] + ".bin" 
            with open(fn, 'wb') as f:
                pickle.dump(self.raw_data, f)


a = FEMB_QC()
FEMB_infos = a.FEMB_QC_Input()
a.FM_QC_PWR( FEMB_infos)



