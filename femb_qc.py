# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Mon May  6 23:34:41 2019
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


class FEMB_QC:
    def __init__(self):
        self.jumbo_flag = False
        self.userdir = "I:/SBND_QC/"
        self.user_f = self.userdir + "FEMB_QCindex.csv"
        self.databkdir = "I:/SBND_QC/FEMB_QC/"
        self.f_qcindex = self.databkdir + "FEMB_QCindex.csv"
        self.femb_qclist = []
        self.WIB_IPs = ["192.168.121.1"]
        self.pwr_n = 10
        self.CLS = CLS_CONFIG()
        self.CLS.WIB_IPs = self.WIB_IPs
        self.CLS.FEMB_ver = 0x501
        self.CLS.jumbo_flag = self.jumbo_flag 
        self.RAW_C = RAW_CONV()
        self.RAW_C.jumbo_flag = self.jumbo_flag 
        self.raw_data = []
        self.env = "RT"
        self.avg_cnt = 0
        with open(self.user_f, 'a') as fp:
            pass
        with open(self.f_qcindex, 'a') as fp:
            pass

    def FEMB_INDEX_LOAD(self):
        self.femb_qclist = []
        with open(self.f_qcindex, 'r') as fp:
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
            femb_ids.append(femb[1])
        return femb_ids

    def FEMB_QC_Input(self):
        FEMBlist = self.FEMB_INDEX_LOAD()
        FEMB_infos = []
        env = self.env
        #env = input("Test is performed at (RT or LN)? :")
        for i in range(4):
            while (True):
                print ("Please enter ID of FEMB in WIB slot%d (input \"OFF\" if no FEMB): "%i)
                FEMB_id = input("Format: FM-AM (e.g. FC1-SAC1) >>")
                cf = input("WIB slot%d with FEMB ID is \"#%s\", Y or N? "%(i, FEMB_id) )
                if (cf == "Y"):
                    break
            c_ret = ""
            if ("OFF" not in FEMB_id):
                c_ret +="ToyTPC14_" + input("Toy TPC NO. for ASIC1-4 : ")
                c_ret +="-ToyTPC58_" +input("Toy TPC NO. for ASIC5-8 : ") + "-"
            if FEMB_id in FEMBlist:
                print ("FEMB \"%s\" has been tested before, please input a short note for this retest"%FEMB_id)
                c_ret += input("Reason for retest: ")
                rerun_f = "Y"
            else:
                rerun_f = "N"
            FEMB_infos.append("SLOT%d"%i + "\n" + FEMB_id + "\n" + env + "\n" + rerun_f + "\n" + c_ret )
        return FEMB_infos

    def FEMB_CHK_ACQ(self, testcode = 0):
        self.CLS.val = 100 
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = False
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()
        testn = testcode % 10
        if testn == 1:
            #14mV/fC, 2.0us, 200mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
        elif testn == 2:
            #7.8mV/fC, 2.0us, 900mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, swdac1=1, swdac2=0, data_cs=0)
        elif testn == 3:
            #7.8mV/fC, 2.0us, 200mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
        elif testn == 4:
            #14mV/fC, 2.0us, 200mV, ASIC_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, asicdac_en=1, sts=1, sg0=0, sg1=1, st0 =1, st1=1, swdac1=0, swdac2=1, dac= 0x08, data_cs=0)
        elif testn == 5:
            #14mV/fC, 2.0us, 200mV, RMS 
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=1)
        elif testn == 6:
            #14mV/fC, 2.0us, 900mV, RMS 
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, sts=0, sg0=0, sg1=1, st0 =1, st1=1, snc=0)
        elif testn == 7:
            #7.8mV/fC, 2.0us, 200mV, RMS 
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, sts=0, sg0=1, sg1=0, st0 =1, st1=1, snc=1)
        elif testn == 8:
            #14mV/fC, 2.0us, 200mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
        elif testn == 9:
            #7.8mV/fC, 2.0us, 200mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=1, sg1=0, st0 =1, st1=1, snc=1, swdac1=1, swdac2=0, data_cs=0)
        else:
            #14mV/fC, 2.0us, 900mV, FPGA_DAC enable = 0x08
            cfglog = self.CLS.CE_CHK_CFG(pls_cs=1, dac_sel=1, fpgadac_en=1, fpgadac_v=0x08, sts=1, sg0=0, sg1=1, st0 =1, st1=1, swdac1=1, swdac2=0, data_cs=0)
        time.sleep(2)
        qc_data = self.CLS.TPC_UDPACQ(cfglog)
        self.CLS.FEMBs_CE_OFF()
        return qc_data

    def FEMB_BL_RB(self,  snc=1, sg0=0, sg1=1, st0 =1, st1=1, slk0=0, slk1=0, sdf=1): #default 14mV/fC, 2.0us, 200mV
        self.CLS.val = 10 
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = False
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()

        w_f_bs = []
        self.CLS.fecfg_loadflg = True
        self.CLS.fe_monflg = True

        for chn in range(128):
            chipn = int(chn//16)
            chipnchn = int(chn%16)
            if (chipnchn == 0):
                print ("Baseline of ASIC%d of all available FEMBs are being measured, wait a while..."%chipn)
            self.CLS.FEREG_MAP.set_fe_board(snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, smn=0, sdf=sdf, slk0=slk0, slk1=slk1 )
            self.CLS.FEREG_MAP.set_fechn_reg(chip=chipn, chn=chipnchn, snc=snc, sg0=sg0, sg1=sg1, st0=st0, st1=st1, smn=1, sdf=sdf )
            self.CLS.REGS = self.CLS.FEREG_MAP.REGS
            cfglog = self.CLS.CE_CHK_CFG(mon_cs = 1)
            for acfg in cfglog:
                w_f_b_new = True
                for i in range(len(w_f_bs)):
                    if w_f_bs[i][0] == acfg[0] and w_f_bs[i][1] == acfg[1] :
                        w_f_bs[i][2].append(acfg[30])
                        w_f_bs[i][3].append(acfg[31])
                        w_f_b_new = False
                        break
                if w_f_b_new :
                    w_f_bs.append([acfg[0], acfg[1], [acfg[30]], [acfg[31]]])

        self.CLS.fecfg_loadflg = False
        self.CLS.fe_monflg = False
        self.CLS.CE_CHK_CFG(mon_cs = 0) #disable monitoring and return to default setting
        self.CLS.FEMBs_CE_OFF()
        return w_f_bs

    def FEMB_Temp_RB(self ):
        self.CLS.val = 10 
        self.CLS.sts_num = 1
        self.CLS.f_save = False
        self.CLS.FM_only_f = False
        self.CLS.WIBs_SCAN()
        self.CLS.FEMBs_SCAN()
        self.CLS.WIBs_CFG_INIT()

        w_f_ts = []
        self.CLS.fecfg_loadflg = True
        self.CLS.fe_monflg = True

        for chip in range(8):
            print ("FE ASIC%d of all available FEMBs are being measured by the monitoring ADC"%chip)
            chipn = chip
            chipnchn = 0

            self.CLS.FEREG_MAP.set_fe_board(smn=0 )
            self.CLS.FEREG_MAP.set_fechip_global(chip=chipn, stb=1, stb1=0 )
            self.CLS.FEREG_MAP.set_fechn_reg(chip=chipn, chn=chipnchn,  smn=1 )
            self.CLS.REGS = self.CLS.FEREG_MAP.REGS
            cfglog = self.CLS.CE_CHK_CFG(mon_cs = 1)
            for acfg in cfglog:
                w_f_t_new = True
                for i in range(len(w_f_ts)):
                    if w_f_ts[i][0] == acfg[0] and w_f_ts[i][1] == acfg[1] :
                        w_f_ts[i][2].append(acfg[30])
                        w_f_ts[i][3].append(acfg[31])
                        w_f_t_new = False
                        break
                if w_f_t_new :
                    w_f_ts.append([acfg[0], acfg[1], [acfg[30]], [acfg[31]]])

        self.CLS.fecfg_loadflg = False
        self.CLS.fe_monflg = False
        self.CLS.CE_CHK_CFG(mon_cs = 0) #disable monitoring and return to default setting
        self.CLS.FEMBs_CE_OFF()
        return w_f_ts
           
    def FEMB_CHK_ANA(self, FEMB_infos, qc_data, pwr_i = 1):
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
                    if (len(er) <=2 ):
                        femb_errlog = "SLOT" + er
                    else:
                        femb_errlog = ("SLOT" + er[0: er.index("#IP")]) if "#IP" in er else ("SLOT" + er[0: ])
                    break

            if  "OFF" in femb_id:
                pass
            else :
                if self.CLS.pwr_int_f:
                    note = "PWR Interruption Enable(0.1s)- " + femb_c_ret
                else:
                    note =  femb_c_ret
                qc_list = ["FAIL", femb_env, femb_id, femb_rerun_f, femb_date, femb_errlog, note, "PWR%d"%pwr_i] 
                map_r = None
                for femb_data in qc_data:
                    if (femb_data[0][1] == femb_addr): 
                        fdata =  femb_data
                        sts_r = fdata[2][0]
                        fembdata = fdata[1]
                        cfg = fdata[0]
                        sts = fdata[2]
                        map_r = self.FEMB_CHK( femb_addr, cfg, fembdata)
                        if (len(femb_errlog) < 8) and map_r[0]:
                            qc_list[0] = "PASS" 
                        else:
                            qc_list[0] = "FAIL" 
                            qc_list[-3] += map_r[1]
                        break
                qcs.append(qc_list )
                if (map_r != None):
                    self.raw_data.append([qc_list, map_r, sts, cfg])
                else:
                    self.raw_data.append([qc_list, None, None, None])
        return qcs

    def FEMB_CHK(self,  femb_addr, cfg, fembdata):
        chn_rmss = []
        chn_peds = []
        chn_pkps = []
        chn_pkns = []
        chn_waves = []
        chn_avg_waves = []
        fpgadac_en = cfg[6]
        asicdac_en = cfg[7]
        fe_sts = cfg[13]
        rms_f = True if ((fpgadac_en==0) and (asicdac_en==0)) or (fe_sts==0) else False

        for adata in fembdata:
            chn_data, feed_loc, chn_peakp, chn_peakn = self.RAW_C.raw_conv_peak(adata)
            for achn in range(len(chn_data)):
                achn_ped = []
                if (rms_f):
                    achn_ped += chn_data[achn] 
                else:
                    for af in range(len(feed_loc[0:-2])):
                        achn_ped += chn_data[achn][feed_loc[af]+100: feed_loc[af+1]-100 ] 
                arms = np.std(achn_ped)
                aped = int(np.mean(achn_ped))
                apeakp = int(np.mean(chn_peakp[achn]))
                apeakn = int(np.mean(chn_peakn[achn]))
                chn_rmss.append(arms)
                chn_peds.append(aped)
                chn_pkps.append(abs(apeakp-aped))
                chn_pkns.append(abs(apeakn-aped))
                chn_waves.append( chn_data[achn][feed_loc[0]: feed_loc[1]] )
                if len(feed_loc) < self.avg_cnt+5:
                    self.avg_cnt = len(feed_loc)-1
                avg_wave = np.array(chn_data[achn][feed_loc[0]: feed_loc[1]]) 
                for i in (1, self.avg_cnt,1):
                    avg_wave += np.array(chn_data[achn][feed_loc[i]: feed_loc[i+1]]) 
                avg_wave = avg_wave/self.avg_cnt
                chn_avg_waves.append(avg_wave)
        ana_err_code = ""
        rms_mean = np.mean(chn_rmss)
        if (rms_f):
            rms_thr = 5*np.std(chn_rmss) if 5*(np.std(chn_rmss) < rms_mean) else rms_mean
            for chn in range(128):
                if abs(chn_rmss[chn] - rms_mean) < rms_thr :
                    pass
                else:
                    ana_err_code += "-F9_RMS_CHN%d"%(chn)

        for gi in range(8): 
            ped_mean = np.mean(chn_peds[gi*16 : (gi+1)*16])
            pkp_mean = np.mean(chn_pkps[gi*16 : (gi+1)*16])
            pkn_mean = np.mean(chn_pkns[gi*16 : (gi+1)*16])
            ped_thr= 30 
            for chn in range(gi*16, (gi+1)*16, 1):
                if abs(chn_peds[chn] - ped_mean) > ped_thr :
                    ana_err_code += "-F9_PED_CHN%d"%(chn)
                if (not rms_f):
                    if chn_pkps[chn] < 200:
                        ana_err_code += "-F9_NORESP_CHN%d"%(chn)
                    if chn_pkns[chn] < 200:
                        ana_err_code += "-F9_NORESN_CHN%d"%(chn)
                    if abs(1- chn_pkps[chn]/pkp_mean) > 0.2:
                        ana_err_code += "-F9_PEAKP_CHN%d"%(chn)
                    if abs(1- chn_pkns[chn]/pkn_mean) > 0.5:
                        ana_err_code += "-F9_PEAKN_CHN%d"%(chn)
        if len(ana_err_code) > 0:
            return (False, ana_err_code, [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves,chn_avg_waves])
        else:
            return (True, "PASS-", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves,chn_avg_waves])

    def FEMB_QC_PWR(self, FEMB_infos, pwr_int_f = False):
        pwr_qcs = []
        self.CLS.pwr_int_f = pwr_int_f
        for pwr_i in range(1, self.pwr_n+1 ):
            print ("Power Cycle %d of %d starts..."%(pwr_i, self.pwr_n))
            qc_data = self.FEMB_CHK_ACQ(testcode = pwr_i)
            qcs = self.FEMB_CHK_ANA(FEMB_infos, qc_data, pwr_i)
            pwr_qcs += qcs
            print ("Power Cycle %d of %d is done, wait 30 seconds"%(pwr_i, self.pwr_n))
            time.sleep(30)
        self.CLS.pwr_int_f = False

        saves = []
        for femb_info in FEMB_infos:
            fembs = femb_info.split("\n")
            femb_id = fembs[1]
            flg = False
            for qct in pwr_qcs:
                if qct[2] == femb_id :
                    if qct[0] == "PASS" :
                        pass_qct = qct
                        flg = True
                    else:
                        flg = False
                        saves.append(qct)
                        break
            if (flg):
                saves.append(pass_qct)

        with open (self.f_qcindex , 'a') as fp:
            print ("Result,ENV,FM_ID,Retun Test,Date,Error_Code,Note,Powr Cycle,")
            for x in saves:
                fp.write(",".join(str(i) for i in x) +  "," + "\n")
                print (x)
        copyfile(self.f_qcindex, self.user_f )

        if (len(pwr_qcs) > 0 ):
            fn =self.databkdir  + "FEMB_QC_" + pwr_qcs[0][1] +"_" + pwr_qcs[0][4] + ".bin" 
            with open(fn, 'wb') as f:
                pickle.dump(self.raw_data, f)
        self.FEMB_PLOT(pwr_int_f = pwr_int_f)
        self.raw_data = []
        print ("Result is saved in %s"%self.user_f )

    def FEMB_SUB_PLOT(self, ax, x, y, title, xlabel, ylabel, color='b', marker='.', atwinx=False, ylabel_twx = "", e=None):
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True)
        if (atwinx):
            ax.errorbar(x,y,e, marker=marker, color=color)
            y_min = int(np.min(y))-1000
            y_max = int(np.max(y))+1000
            ax.set_ylim([y_min, y_max])
            ax2 = ax.twinx()
            ax2.set_ylabel(ylabel_twx)
            ax2.set_ylim([int((y_min/16384.0)*2048), int((y_max/16384.0)*2048)])
        else:
            ax.plot(x,y, marker=marker, color=color)

    def FEMB_PLOT(self, pwr_int_f = False):
        import matplotlib.pyplot as plt
        if len(self.raw_data) != 0: 
            for a_femb_data in self.raw_data:
                qc_list = a_femb_data[0]
                qc_pf = qc_list[0]
                env = qc_list[1]
                femb_id = qc_list[2]
                femb_rerun_f = qc_list[3]
                femb_date = qc_list[4]
                femb_errlog = qc_list[5]
                femb_c_ret = qc_list[6]
                femb_pwr = qc_list[7]

                png_dir = self.databkdir + "/" + femb_id + "/"
                if (os.path.exists(png_dir)):
                    pass
                else:
                    try:
                        os.makedirs(png_dir)
                    except OSError:
                        print ("Error to create folder %s"%png_dir)
                        sys.exit()
                fn = png_dir + "/" + env + "_" + femb_id + "_" + femb_date + "_" + femb_pwr + ".png"

                fig = plt.figure(figsize=(8.5,11))
                color = "g" if "PASS" in qc_pf else "r"
                fig.suptitle("Test Result of Power Cycle #%s (%s)"%(femb_pwr[-1], qc_pf), color=color, weight ="bold", fontsize = 12)
                fig.text(0.10, 0.94, "Date&Time: %s"%femb_date   )
                fig.text(0.55, 0.94, "Temperature: %s "%env  )
                fig.text(0.10, 0.92, "FEMB ID: %s "%femb_id      )
                fig.text(0.55, 0.92, "STATUS: %s "%qc_pf, color=color, weight ="bold" )
                fig.text(0.10,0.90, "Rerun comment: %s "%femb_c_ret     )

                map_r = a_femb_data[1]
                if (map_r != None):
                    map_pf = map_r[0]
                    map_pf_str = map_r[1]
                    chn_rmss = map_r[2][0] # 128chn list, each element is a integal
                    chn_peds = map_r[2][1] # 128chn list, each element is a float
                    chn_pkps = map_r[2][2] # 128chn list, each element is a integal
                    chn_pkns = -(abs(np.array(map_r[2][3]))) # 128chn list, each element is a integal
                    chn_wfs  = map_r[2][4] # 128chn list, each element is a list
                    d_sts = a_femb_data[2][0]
                    d_sts_keys = list(d_sts.keys())
                    wib_ip = a_femb_data[3][0]
                    femb_addr = a_femb_data[3][1]

                    fpgadac_en = a_femb_data[3][6]
                    asicdac_en = a_femb_data[3][7]
                    fpgadac_v  = a_femb_data[3][8]
                    snc  = a_femb_data[3][14]
                    sg0  = a_femb_data[3][15]
                    sg1  = a_femb_data[3][16]
                    st0  = a_femb_data[3][17]
                    st1  = a_femb_data[3][18]
                    sdf  = a_femb_data[3][20]
                    asicdac_v = a_femb_data[3][29]
                    if fpgadac_en:
                        cali_str = "FPGA-DAC(%02x)"%fpgadac_v
                    elif asicdac_en:
                        cali_str = "ASIC-DAC(%02x)"%asicdac_v
                    else:
                        cali_str = "No pulser"
                    snc_str = "FE Baseline 200mV" if snc==1 else "FE Baseline 900mV"
                    sdf_str = "FE Buffer ON" if sdf==1 else "FE Buffer OFF"
                    if sg0 == 0 and sg1 == 0:
                        sg_str = "4.7mV/fC"
                    elif sg0 == 1 and sg1 == 0:
                        sg_str = "7.8mV/fC"
                    elif sg0 == 0 and sg1 == 1:
                        sg_str = "14mV/fC"
                    else:
                        sg_str = "25mV/fC"

                    if st0 == 0 and st1 == 0:
                        st_str = "1.0$\mu$s"
                    elif st0 == 1 and st1 == 0:
                        st_str = "0.5$\mu$s"
                    elif st0 == 0 and st1 == 1:
                        st_str = "3.0$\mu$s"
                    else:
                        st_str = "2.0$\mu$s"
               
                    fembsts_keys = []
                    for akey in d_sts_keys:
                        if (akey == "FEMB%d"%femb_addr):
                            fembsts_keys.append(akey)
                
                    fig.text(0.10, 0.88, "WIB IP: %s "%wib_ip      )
                    fig.text(0.55, 0.88, "FEMB SLOT: %s "%femb_addr     )
                    fig.text(0.10, 0.86, "FE Configuration: " + sg_str + ", " + st_str + ", " + snc_str + ", " + sdf_str + ", " + cali_str  )

                    fig.text(0.35, 0.83, "Link Status and Power consumption" ,weight ="bold"    )
                    fig.text(0.10, 0.81, "LINK: : " + "{0:4b}".format(d_sts["FEMB%d_LINK"%femb_addr])   )
                    fig.text(0.55, 0.81, "EQ: : " + "{0:4b}".format(d_sts["FEMB%d_EQ"%femb_addr])      )
                    fig.text(0.10, 0.79, "Checksum error counter of LINK0 to LINK3 : %04X, %04X, %04X, %04X"%\
                                          (d_sts["FEMB%d_CHK_ERR_LINK0"%femb_addr], d_sts["FEMB%d_CHK_ERR_LINK1"%femb_addr] ,
                                           d_sts["FEMB%d_CHK_ERR_LINK2"%femb_addr], d_sts["FEMB%d_CHK_ERR_LINK3"%femb_addr] ) )
                    fig.text(0.10, 0.77, "Frame error counter of LINK0 to LINK3 : %04X, %04X, %04X, %04X"% \
                                          (d_sts["FEMB%d_FRAME_ERR_LINK0"%femb_addr], d_sts["FEMB%d_FRAME_ERR_LINK1"%femb_addr] ,
                                           d_sts["FEMB%d_FRAME_ERR_LINK2"%femb_addr], d_sts["FEMB%d_FRAME_ERR_LINK3"%femb_addr] ) )
                    fig.text(0.10, 0.75, "FEMB Power Consumption = " + "{0:.4f}".format(d_sts["FEMB%d_PC"%femb_addr]) + "W" )
                    if (pwr_int_f):
                        fig.text(0.55, 0.75, "Power 0.1s Interruption Enabled", color ='r' )

                    fig.text(0.10, 0.73, "BIAS = " + "{0:.4f}".format(d_sts["FEMB%d_BIAS_V"%femb_addr]) + \
                                         "V, AM V33 = " + "{0:.4f}".format(d_sts["FEMB%d_AMV33_V"%femb_addr]) + \
                                         "V, AM V28 = " + "{0:.4f}".format(d_sts["FEMB%d_AMV28_V"%femb_addr]) + "V")

                    fig.text(0.10, 0.71, "BIAS = " + "{0:.4f}".format(d_sts["FEMB%d_BIAS_I"%femb_addr]) + \
                                         "A, AM V33 = " + "{0:.4f}".format(d_sts["FEMB%d_AMV33_I"%femb_addr]) + \
                                         "A, AM V28 = " + "{0:.4f}".format(d_sts["FEMB%d_AMV28_I"%femb_addr]) + "A")

                    fig.text(0.10, 0.69, "FM V39 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV39_V"%femb_addr]) + \
                                         "V, FM V30 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV30_V"%femb_addr]) + \
                                         "V, FM V18 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV18_V"%femb_addr]) + "V" )

                    fig.text(0.10, 0.67, "FM V39 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV39_I"%femb_addr]) + \
                                         "A, FM V30 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV30_I"%femb_addr]) + \
                                         "A, FM V18 = " + "{0:.4f}".format(d_sts["FEMB%d_FMV18_I"%femb_addr]) + "A" )
                
                
                    ax1 = plt.subplot2grid((4, 2), (2, 0), colspan=1, rowspan=1)
                    ax2 = plt.subplot2grid((4, 2), (3, 0), colspan=1, rowspan=1)
                    ax3 = plt.subplot2grid((4, 2), (2, 1), colspan=1, rowspan=1)
                    ax4 = plt.subplot2grid((4, 2), (3, 1), colspan=1, rowspan=1)
                    chns = range(len(chn_rmss))
                    if (self.avg_cnt)<=1:
                        self.FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
                        self.FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Pedestal", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
                        self.FEMB_SUB_PLOT(ax3, chns, chn_pkps, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
                        self.FEMB_SUB_PLOT(ax3, chns, chn_pkns, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='g', marker='.')
                        for chni in chns:
                            ts = 100 if (len(chn_wfs[chni]) > 100) else len(chn_wfs[chni])
                            x = (np.arange(ts)) * 0.5
                            y = chn_wfs[chni][0:ts]
                            self.FEMB_SUB_PLOT(ax4, x, y, title="Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))
                    else:
                        chn_avg_wfs  = map_r[2][5] # 128chn list, each element is a list
                        self.FEMB_SUB_PLOT(ax1, chns, chn_peds, title="Pedestal", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
                        self.FEMB_SUB_PLOT(ax2, chns, chn_pkps, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
                        self.FEMB_SUB_PLOT(ax2, chns, chn_pkns, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='g', marker='.')
                        for chni in chns:
                            ts = 100 if (len(chn_wfs[chni]) > 100) else len(chn_wfs[chni])
                            x = (np.arange(ts)) * 0.5
                            y1 = chn_wfs[chni][0:ts]
                            self.FEMB_SUB_PLOT(ax3, x, y1, title="Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))
                            y2 = chn_avg_wfs[chni][0:ts]
                            self.FEMB_SUB_PLOT(ax4, x, y2, title="Averaging Waveform Overlap ", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))

                if ("PASS" not in qc_pf):
                    cperl = 80
                    lines = int(len(femb_errlog)//cperl) + 1
                    fig.text(0.05,0.65, "Error log: ")
                    printlines =  lines if lines<=5 else 5
                    for i in range(printlines):
                        fig.text(0.10, 0.63-0.02*i, femb_errlog[i*cperl:(i+1)*cperl])
                    if (lines>5):
                        fig.text(0.10, 0.63-0.02*5, " ... ... ... (%d more lines are not shown!)"%(lines-5) )
                
                plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                plt.savefig(fn)
                plt.close()

    def QC_FEMB_BL_T_PLOT(self, FEMB_infos, pwr_int_f = False):
        self.CLS.pwr_int_f = pwr_int_f
        w_f_bs_200mV = self.FEMB_BL_RB(snc=1, sg0=0, sg1=1, st0 =1, st1=1, slk0=0, slk1=0, sdf=1) # 14mV/fC, 2.0us, 200mV
        w_f_bs_900mV = self.FEMB_BL_RB(snc=0, sg0=0, sg1=1, st0 =1, st1=1, slk0=0, slk1=0, sdf=1) # 14mV/fC, 2.0us, 900mV
        w_f_ts = self.FEMB_Temp_RB()
        self.CLS.pwr_int_f = False
        BL_T_data = []

        for femb_info in FEMB_infos:
            fembs = femb_info.split("\n")
            femb_addr = int(fembs[0][4])
            femb_id = fembs[1]
            femb_env = fembs[2]
            femb_rerun_f = fembs[3]
            femb_c_ret = fembs[4]
            femb_date = self.CLS.err_code[self.CLS.err_code.index("#TIME") +5: self.CLS.err_code.index("#IP")] 
            errs = self.CLS.err_code.split("SLOT")
            wib_ip = self.CLS.err_code[self.CLS.err_code.index("#IP") +3: self.CLS.err_code.index("-SLOT")] 
            for er in errs[1:]:
                if( int(er[0]) == femb_addr ):
                    if (len(er) <=2 ):
                        femb_errlog = "SLOT" + er
                    else:
                        femb_errlog = ("SLOT" + er[0: er.index("#IP")]) if "#IP" in er else ("SLOT" + er[0: ])
                    break

            if  "OFF" in femb_id:
                pass
            else :
                ys = []
                ys_std = []
                for w_fs in [w_f_bs_200mV, w_f_bs_900mV, w_f_ts]:
                #for w_fs in [w_f_ts, w_f_ts, w_f_ts]:
                    for f_bt in w_fs:
                        if f_bt[0] == wib_ip and f_bt[1] == femb_addr:
                            ys.append(f_bt[2])
                            ys_std.append(f_bt[3])
                            break
                BL_T_data.append([femb_id, ys, wib_ip, femb_addr, femb_env, femb_rerun_f, femb_c_ret, femb_date, femb_errlog]) 
                import matplotlib.pyplot as plt
                png_dir = self.databkdir + "/" + femb_id + "/"
                if (os.path.exists(png_dir)):
                    pass
                else:
                    try:
                        os.makedirs(png_dir)
                    except OSError:
                        print ("Error to create folder %s"%png_dir)
                        sys.exit()
                fn_fig = png_dir + "BL_T_" + femb_env + "_" + femb_id + "_" + femb_date +  ".png"
                fig = plt.figure(figsize=(8.5,11))
                fig.suptitle("BASELINE and Temperature Measurement of FEMB#%s"%(femb_id), weight ="bold", fontsize = 12)
                fig.text(0.10, 0.94, "Date&Time: %s"%femb_date   )
                fig.text(0.55, 0.94, "Temperature: %s "%femb_env  )
                fig.text(0.10, 0.92, "FEMB ID: %s "%femb_id      )
                fig.text(0.10,0.90, "Rerun comment: %s "%femb_c_ret     )
                fig.text(0.10, 0.88, "WIB IP: %s "%wib_ip      )
                fig.text(0.55, 0.88, "FEMB SLOT: %s "%femb_addr     )
                if (pwr_int_f):
                    fig.text(0.10, 0.86, "Power 0.1s Interruption Enabled", color ='r' )
                if len(femb_errlog) < 8:
                    ax1 = plt.subplot2grid((4, 1), (1, 0), colspan=1, rowspan=1)
                    ax2 = plt.subplot2grid((4, 1), (2, 0), colspan=1, rowspan=1)
                    ax3 = plt.subplot2grid((4, 1), (3, 0), colspan=1, rowspan=1)
                    self.FEMB_SUB_PLOT(ax1, range(len(ys[0])), ys[0], title="FE 200mV Baseline Measurement", \
                                       xlabel="CH number", ylabel ="MON ADC / bin", color='r', marker='.', \
                                       atwinx=True, ylabel_twx = "Amplitude / mV", e=ys_std[0] )
                    self.FEMB_SUB_PLOT(ax2, range(len(ys[1])), ys[1], title="FE 900mV Baseline Measurement", \
                                       xlabel="CH number", ylabel ="MON ADC / bin", color='r', marker='.', \
                                       atwinx=True, ylabel_twx = "Amplitude / mV", e=ys_std[1])
                    self.FEMB_SUB_PLOT(ax3, range(len(ys[2])), ys[2], title="Temperature Readout From FE", \
                                       xlabel="FE number (CHN0 of a FE ASIC)", ylabel ="MON ADC / bin", color='r', marker='.',\
                                       atwinx=True, ylabel_twx = "Amplitude / mV", e=ys_std[2])
                else:
                    cperl = 80
                    lines = int(len(femb_errlog)//cperl) + 1
                    fig.text(0.05,0.65, "Error log: ")
                    for i in range(lines):
                        fig.text(0.10, 0.63-0.02*i, femb_errlog[i*cperl:(i+1)*cperl])
                
                plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
                plt.savefig(fn_fig)
                print (fn_fig)
                plt.close()

        femb_date = self.CLS.err_code[self.CLS.err_code.index("#TIME") +5: self.CLS.err_code.index("#IP")] 
        fn =self.databkdir  + "FEMB_QC_BL_T_"  + femb_date + ".bin" 
        with open(fn, 'wb') as f:
            pickle.dump(BL_T_data, f)

    def FEMB_CHKOUT_Input(self):
        FEMBlist = self.FEMB_INDEX_LOAD()
        FEMB_infos = []
        env = self.env
        for i in range(4):
            while (True):
                print ("Please enter ID of FEMB(AM) in WIB slot%d (input \"OFF\" if no FEMB): "%i)
                FEMB_id = input("(e.g. TAC01) >>")
                cf = input("WIB slot%d with FEMB ID is \"#%s\", Y or N? "%(i, FEMB_id) )
                if (cf == "Y"):
                    break
            c_ret = ""
            rerun_f = "N"
            FEMB_infos.append("SLOT%d"%i + "\n" + FEMB_id + "\n" + env + "\n" + rerun_f + "\n" + c_ret )
        return FEMB_infos

    def FEMB_CHKOUT(self, FEMB_infos, pwr_int_f = False, testcode = 1):
        pwr_qcs = []
        self.CLS.pwr_int_f = pwr_int_f
        qc_data = self.FEMB_CHK_ACQ(testcode = testcode)
        qcs = self.FEMB_CHK_ANA(FEMB_infos, qc_data, pwr_i=testcode)
        pwr_qcs += qcs
        self.CLS.pwr_int_f = False
        if (len(pwr_qcs) > 0 ):
            fn =self.databkdir  + "FEMB_CHKOUT_" + pwr_qcs[0][1] +"_" + pwr_qcs[0][4] + ".bin" 
            with open(fn, 'wb') as f:
                pickle.dump(self.raw_data, f)
        self.FEMB_PLOT(pwr_int_f = pwr_int_f)
        self.raw_data = []
        print ("Result is saved in %s"%self.user_f )



a = FEMB_QC()
a.env = "RT"
FEMB_infos = a.FEMB_CHKOUT_Input()
a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 1 )
print ("Well Done")

##warm test
#flg = "N"
#while ( "Y" not in flg):
#    time.sleep(2)
#    flg = input("Is Warm Test Ready(Y)?")
#if "Y" in flg:
#    a.FEMB_QC_PWR( FEMB_infos)
#    a.QC_FEMB_BL_T_PLOT(FEMB_infos)
#
##cold test
#flg = "N"
#while ( "Y" not in flg):
#    time.sleep(2)
#    flg = input("Is Cold Test Ready(Y)?")
#if "Y" in flg:
#    a.env = "LN"
#    if ("LN" in FEMB_infos[0]):
#        a.FEMB_QC_PWR( FEMB_infos, pwr_int_f = True)
#        a.QC_FEMB_BL_T_PLOT(FEMB_infos, pwr_int_f = True)
#    a.FEMB_QC_PWR( FEMB_infos)
#    a.QC_FEMB_BL_T_PLOT(FEMB_infos)




#FEMB_infos = ['SLOT0\nFC1-SAC1\nRT\nN\n', 'SLOT1\nFC2-SAC2\nRT\nN\n', 'SLOT2\nFC3-SAC3\nRT\nN\n', 'SLOT3\nFC4-SAC4\nRT\nN\n']
#FEMB_infos = ['SLOT0\nFC022-TAC01\nRT\nN\n', 'SLOT1\nFC026-TAC02\nRT\nN\n', 'SLOT2\nFC037-TAC03\nRT\nN\n', 'SLOT3\nFC024-TAC04\nRT\nN\n']
#FEMB_infos = ['SLOT0\nFC022-TAC01\nLN\nN\n', 'SLOT1\nFC026-TAC02\nLN\nN\n', 'SLOT2\nFC037-TAC03\nLN\nN\n', 'SLOT3\nFC024-TAC04\nLN\nN\n']
#FEMB_infos = ['SLOT0\nFC1-SAC1\nRT\nN\n', 'SLOT1\nFC2-SAC2\nRT\nN\n', 'SLOT2\nFC3-SAC3\nRT\nN\n', 'SLOT3\nFC4-SAC4\nRT\nN\n']
#a.FEMB_QC_PWR( FEMB_infos)
#a.FEMB_PLOT()
#a.QC_FEMB_BL_T_PLOT(FEMB_infos)
#a.FEMB_BL_RB(snc=1, sg0=0, sg1=1, st0 =1, st1=1, slk0=0, slk1=0, sdf=1) #default 14mV/fC, 2.0us, 200mV
#1a.FEMB_Temp_RB()
#a.FEMB_BL_RB() #default 14mV/fC, 2.0us, 200mV
#fn =a.databkdir  + "\FM_QC_RT_2019_04_09_18_26_28.bin"
#FEMB_QC_RT_2019_04_23_19_57_46
#with open(fn, 'rb') as f:
#     a.raw_data = pickle.load(f)
 



