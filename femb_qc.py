# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 2/22/2024 11:30:37 AM
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
        self.userdir = "D:/SBND_CHKOUT/"
        self.femb_qclist = []
        self.WIB_IPs = ["192.168.121.1"]
        self.pwr_n = 10
        self.raw_data = []
        self.env = "RT"
        self.avg_cnt = 0
        self.CLS = CLS_CONFIG()
        self.RAW_C = RAW_CONV()

    def init_cfg(self):
        self.user_f = self.userdir + "FEMB_CHKOUT_index.csv"
        self.databkdir = self.userdir + "/BAK/"
        self.f_qcindex = self.databkdir + "FEMB_CHKOUT_index.csv"
        self.CLS.WIB_IPs = self.WIB_IPs
        self.CLS.FEMB_ver = 0x407
        self.CLS.jumbo_flag = self.jumbo_flag 
        self.CLS.UDP.jumbo_flag = self.jumbo_flag 
        self.RAW_C.jumbo_flag = self.jumbo_flag 

        if (os.path.exists(self.userdir)):
            pass
        else:
            try:
                os.makedirs(self.userdir)
            except OSError:
                print ("Error to create folder %s"%png_dir)
                sys.exit()

        if (os.path.exists(self.databkdir)):
            pass
        else:
            try:
                os.makedirs(self.databkdir)
            except OSError:
                print ("Error to create folder %s"%png_dir)
                sys.exit()

        if (os.path.isfile(self.f_qcindex)):
           with open(self.f_qcindex, 'a') as fp:
                pass
           with open(self.user_f, 'a') as fp:
                pass
        else:
            copyfile("./FEMB_CHKOUT_index.csv", self.f_qcindex )
            copyfile(self.f_qcindex, self.user_f )

    def FEMB_CHK_ACQ(self, testcode = 0):
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
                qc_list = ["FAIL", femb_env, femb_id, femb_rerun_f, femb_date, femb_errlog, note, "%d"%pwr_i] 
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
                for i in range(1, self.avg_cnt,1):
                    avg_wave =avg_wave + np.array(chn_data[achn][feed_loc[i]: feed_loc[i+1]]) 
                avg_wave = avg_wave/self.avg_cnt
                chn_avg_waves.append(avg_wave)
        ana_err_code = ""
        rms_mean = np.mean(chn_rmss)
        if (rms_f):
            rms_thr = 5*np.std(chn_rmss) if 5*(np.std(chn_rmss) < rms_mean) else rms_mean
            for chn in range(128):
                if abs(chn_rmss[chn] - rms_mean) < rms_thr :
                    pass
#                else:
#                    ana_err_code += "-F9_RMS_CHN%d"%(chn)

        for gi in range(8): 
            ped_mean = np.mean(chn_peds[gi*16 : (gi+1)*16])
            pkp_mean = np.mean(chn_pkps[gi*16 : (gi+1)*16])
            pkn_mean = np.mean(chn_pkns[gi*16 : (gi+1)*16])
            ped_thr= 100 
            for chn in range(gi*16, (gi+1)*16, 1):
                if abs(chn_peds[chn] - ped_mean) > ped_thr :
                    ana_err_code += "-F9_PED_CHN%d"%(chn)
                if (not rms_f):
                    if chn_pkps[chn] < 200:
                        ana_err_code += "-F9_NORESP_CHN%d"%(chn)
#                    if chn_pkns[chn] < 200:
#                        ana_err_code += "-F9_NORESN_CHN%d"%(chn)
                    if abs(1- chn_pkps[chn]/pkp_mean) > 0.2:
                        ana_err_code += "-F9_PEAKP_CHN%d"%(chn)
#                    if abs(1- chn_pkns[chn]/pkn_mean) > 0.5:
#                        ana_err_code += "-F9_PEAKN_CHN%d"%(chn)
        if len(ana_err_code) > 0:
            return (False, ana_err_code, [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves,chn_avg_waves])
        else:
            return (True, "PASS-", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_waves,chn_avg_waves])

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

                png_dir = self.userdir + "/" + femb_id + "/"
                if (os.path.exists(png_dir)):
                    pass
                else:
                    try:
                        os.makedirs(png_dir)
                    except OSError:
                        print ("Error to create folder %s"%png_dir)
                        sys.exit()
                fn = png_dir + "/" +  femb_id + "_" + env +  "_" + femb_date + "_" + ".png"

                fig = plt.figure(figsize=(8.5,11))
                color = "g" if "PASS" in qc_pf else "r"
                fig.suptitle("Test Result of Test Mode #%s (%s)"%(femb_pwr[-1], qc_pf), color=color, weight ="bold", fontsize = 12)
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
                            ts1 = 100 if (len(chn_wfs[chni]) > 100) else len(chn_wfs[chni])
                            x1 = (np.arange(ts1)) * 0.5
                            y1 = chn_wfs[chni][0:ts1]
                            self.FEMB_SUB_PLOT(ax3, x1, y1, title="Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))

                            ts2 = 100 if (len(chn_wfs[chni]) > 100) else len(chn_wfs[chni])
                            x2 = (np.arange(ts2)) * 0.5
                            y2 = chn_avg_wfs[chni][0:ts2]
                            self.FEMB_SUB_PLOT(ax4, x2, y2, title="Averaging (%d) Waveform Overlap"%self.avg_cnt, xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))

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

    def FEMB_CHKOUT_Input(self):
        FEMB_infos = []
        env = self.env
        while True:
            try :
                fembslotno = int(input("FEMB on WIB Slot# (1-4) :"))
                if (1<= fembslotno) and (fembslotno <=4):
                    self.CLS.femb_sws[fembslotno-1] = 1
                    break
            except OSError:
                print ("Please input a number between 1 to 4 according to which WIB slot is attached with a FEMB")

        for i in range(4):
            if self.CLS.femb_sws[i] == 1:
                while (True):
                    print ("Please enter ID of FEMB(AM) in WIB slot%d (input \"OFF\" if no FEMB): "%i)
                    FEMB_id = input("(e.g. TAC01) >>")
                    cf = input("WIB slot%d with FEMB ID is \"#%s\", Y or N? "%(i, FEMB_id) )
                    if (cf == "Y"):
                        break
            else:
                FEMB_id = "OFF"
            c_ret = "-"
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
            print ("Result,ENV,FM_ID,Retun Test,Date,Error_Code,Note,Test Mode,")
            for x in saves:
                fp.write(",".join(str(i) for i in x) +  "," + "\n")
                print (x)
        copyfile(self.f_qcindex, self.user_f )

        if (len(pwr_qcs) > 0 ):
            fn =self.databkdir  + "FEMB_CHKOUT_" + pwr_qcs[0][1] +"_" + pwr_qcs[0][4] + ".bin" 
            with open(fn, 'wb') as f:
                pickle.dump(self.raw_data, f)
        self.FEMB_PLOT(pwr_int_f = pwr_int_f)
        self.raw_data = []
        print ("Result is saved in %s"%self.user_f )

