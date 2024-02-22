# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 2/22/2024 10:54:08 AM
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
from cls_udp import CLS_UDP
from fe_reg_mapping import FE_REG_MAPPING
import pickle

class CLS_CONFIG:
    def __init__(self):
        self.jumbo_flag = False 
        self.FEMB_ver = 0x407
        self.WIB_ver = 0x120
        self.WIB_IPs = ["192.168.121.1", "192.168.121.2", "192.168.121.3", \
                        "192.168.121.4", "192.168.121.5", "192.168.121.6",] #WIB IPs connected to host-PC
        self.MBB_IP  = "192.168.121.10"
        self.act_fembs = {}
        self.UDP = CLS_UDP()
        self.UDP.jumbo_flag = self.jumbo_flag
        self.Int_CLK = True
        self.pllfile ="./Si5344-RevD-SBND_V2-100MHz_REVD_PTC.txt" 
        self.fecfg_f ="./fecfg.csv" 
        self.FEREG_MAP = FE_REG_MAPPING()
        self.DAQstream_en =  True
        self.pwr_dly = 5 #delay(s) after power operation
        self.sts_num = 1 #how many times statitics data are collected
        self.val = 100 #how many UDP HS package are collected per time
        self.f_save = False #if False, no raw data is saved, if True, no further data analysis 
        self.savedir = "./" 
        self.FM_only_f = False #Only FM, no AM
        self.err_code = ""
        self.fecfg_loadflg = False
        self.fe_monflg = False
        self.femb_sws = [0,0,0,0]
        self.REGS = []
        self.pwr_int_f = False #only set to "True" for FEMB screening test

    def WIB_UDP_CTL(self, wib_ip, WIB_UDP_EN = False):
        self.UDP.UDP_IP = wib_ip
        wib_reg_7_value = self.UDP.read_reg_wib (7)
        if (WIB_UDP_EN): #enable UDP output
            wib_reg_7_value = wib_reg_7_value & 0x00000000 #bit31 of reg7 for disable wib udp control
        else: #disable WIB UDP output
            wib_reg_7_value = wib_reg_7_value | 0x80000000 #bit31 of reg7 for disable wib udp control
        self.UDP.write_reg_wib_checked (7, wib_reg_7_value)

    def WIBs_SCAN(self, wib_verid=0x109):
        print ("Finding available WIBs starts...")
        active_wibs = []
        for wib_ip in self.WIB_IPs:
            self.UDP.UDP_IP = wib_ip
            for i in range(5):
                wib_ver_rb = self.UDP.read_reg_wib (0xFF)
                wib_ver_rb = self.UDP.read_reg_wib (0xFF)
                if ((wib_ver_rb&0x0F00) == wib_verid&0x0F00) and ( wib_ver_rb >= 0):
                    print ("WIB with IP = %s is found"%wib_ip) 
                    active_wibs.append(wib_ip)
                    break
                elif ( wib_ver_rb == -2):
                    print ("Timeout. WIB with IP = %s isn't mounted, mask this IP"%wib_ip) 
                    break
                time.sleep(0.1)
                if (i == 4):
                    print ("WIB with IP = %s get error (%x readback from CLS_UDP.read_reg()), mask this IP"%(wib_ip, wib_ver_rb)) 
            self.WIB_UDP_CTL( wib_ip, WIB_UDP_EN = False)
        self.WIB_IPs = active_wibs

        if len(active_wibs) == 0:
            print ("No WIB is availabe, please check power for WIB is ON! Exit Anyway!")
            sys.exit()
        else:
            print ("WIB scanning is done" )

    def WIB_PWR_FEMB(self, wib_ip, femb_sws=[1,1,1,1]):
        print ("FEMBs power operation on the WIB with IP = %s, wait a moment"%wib_ip)
        self.UDP.UDP_IP = wib_ip
        if (self.pwr_int_f):
            pwr_ctl = [0x31000F, 0x5200F0, 0x940F00, 0x118F000]
            pwr_wr = 0
            for i in range(len(femb_sws)):
                if ( femb_sws[i] == 1):
                    pwr_wr |= np.uint32(pwr_ctl[i])
                else:
                    pwr_wr |= 0
            self.UDP.write_reg_wib_checked (0x8, 0) #All off
            time.sleep(5)
            self.UDP.write_reg_wib_checked (0x8, pwr_wr) 
            time.sleep(5)
            self.UDP.write_reg_wib_checked (0x8, 0) #All off
            time.sleep(0.1)
            self.UDP.write_reg_wib_checked (0x8, pwr_wr)
        else:
            pwr_status = self.UDP.read_reg_wib (0x8)
            pwr_ctl = [0x31000F, 0x5200F0, 0x940F00, 0x118F000]
            for i in range(len(femb_sws)):
                if ( femb_sws[i] == 1):
                    pwr_status |= np.uint32(pwr_ctl[i])
                    self.UDP.write_reg_wib_checked (0x8, pwr_status )
                    time.sleep(1)
                else:
                    if (i == 3) and (femb_sws == [0, 0, 0, 0]):
                        pwr_status = 0x00000000
                    else:
                        pwr_status &= (~np.uint32(pwr_ctl[i]) | 0x00100000)
                    self.UDP.write_reg_wib_checked (0x8, pwr_status )
                    time.sleep(1)
        print ("Wait 5s...")
        time.sleep(self.pwr_dly)

    def FEMB_DECTECT(self, wib_ip):
        self.UDP.UDP_IP = wib_ip
        self.WIB_PWR_FEMB(wib_ip, femb_sws=self.femb_sws)
        stats = self.WIB_STATUS(wib_ip)
        keys = list(stats.keys())
        fembs_found = [True, True, True, True]
        for i in range(4):
            if self.femb_sws[i] != 0:
                fembs_found[i] = True
            else:
                fembs_found[i] = False
        
        self.err_code += "#TIME" + stats["TIME"]
        for i in range(4):
            if fembs_found[i] == False:
                continue
            self.err_code +="#IP" + wib_ip + "-SLOT%d"%i
            for key in keys:
                if key in "FEMB%d_LINK"%i:
                    if (stats[key] != 0xFF):
                        print ("FEMB%d LINK is broken!"%i)
                        fembs_found[i] = False
                        self.err_code += "-F2_LINK"
                elif key in "FEMB%d_EQ"%i:
                    if (stats[key] != 0xF):
                        print ("FEMB%d EQ is broken!"%i)
                        fembs_found[i] = False
                        self.err_code += "-F3_EQ"
                elif key in "FEMB%d_BIAS_I"%i:
                    if (stats[key] < 0.001 ):
                        print ("FEMB%d BIAS current (%fA) is lower than expected"%(i, stats[key]) )
                        fembs_found[i] = False
                        self.err_code +="-F1_BIAS_L"
                    elif (stats[key] > 0.1 ):
                        print ("FEMB%d BIAS current (%fA) is higher than expected"%(i, stats[key]) )
                        fembs_found[i] = False
                        self.err_code += "-F1_BIAS_H"
                elif key in "FEMB%d_FMV39_I"%i:
                    if (stats[key] < 0.010 ):
                        print ("FEMB%d FM_V39 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                        self.err_code += "-F1_FMV39_L"
                    elif (stats[key] > 0.2 ):
                        print ("FEMB%d FM_V39 current (%fA) is higher than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                        self.err_code += "-F1_FMV39_H"
                elif key in "FEMB%d_FMV30_I"%i:
                    if (stats[key] < 0.050 ):
                        print ("FEMB%d FM_V30 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                        self.err_code += "-F1_FMV30_L"
                    elif (stats[key] > 0.5 ):
                        print ("FEMB%d FM_V30 current (%fA) is higher than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                        self.err_code += "-F1_FMV30_H"
                elif key in "FEMB%d_FMV18_I"%i:
                    if (stats[key] < 0.200 ):
                        print ("FEMB%d FM_V18 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                        self.err_code += "-F1_FMV18_L"
                    elif (stats[key] > 1.0 ):
                        print ("FEMB%d FM_V18 current (%fA) is higher than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                        self.err_code += "-F1_FMV18_H"
                elif key in "FEMB%d_AMV33_I"%i:
                    if (stats[key] < 0.100 ):
                        print ("FEMB%d AM_V33 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False if not self.FM_only_f else True
                        self.err_code +="-F1_AMV33_L"if not self.FM_only_f else ""
                    elif (stats[key] > 1.0 ):
                        print ("FEMB%d AM_V33 current (%fA) is higher than expected"%(i, stats[key] ))
                        fembs_found[i] = False if not self.FM_only_f else True
                        self.err_code +="-F1_AMV33_H"if not self.FM_only_f else ""
                elif key in "FEMB%d_AMV28_I"%i:
                    if (stats[key] < 0.100 ):
                        print ("FEMB%d AM_V28 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False if not self.FM_only_f else True
                        self.err_code +="-F1_AMV28_L"if not self.FM_only_f else ""
                    elif (stats[key] > 1.5 ):
                        print ("FEMB%d AM_V28 current (%fA) is higher than expected"%(i, stats[key] ))
                        fembs_found[i] = False if not self.FM_only_f else True
                        self.err_code +="-F1_AMV28_H"if not self.FM_only_f else ""
            if (fembs_found[i]): #Link and current are good
                self.UDP.write_reg_femb(i, 0x0, 0x0)
                self.UDP.read_reg_femb(i, 0x102)
                ver_value = self.UDP.read_reg_femb(i, 0x101)
                if (ver_value > 0 ):
                    if (ver_value&0xFFF != self.FEMB_ver):
                        print ("FEMB%d FE version is %x, which is different from default (%x)!"%(i, ver_value, self.FEMB_ver))
                        fembs_found[i] = False
                        self.err_code +="-F7_FW"
                elif (ver_value <= 0 ):
                    print ("I2C of FEMB%d is broken"%i)
                    fembs_found[i] = False
                    self.err_code +="-F4_I2C"
        self.act_fembs[wib_ip] = fembs_found
        print (self.act_fembs)
        self.WIB_PWR_FEMB(wib_ip, femb_sws=[0,0,0,0])
        return self.err_code

    def WIB_STATUS(self, wib_ip):
        runtime =  datetime.now().strftime('%Y_%m_%d_%H_%M_%S') 
        self.UDP.UDP_IP = wib_ip
        status_dict = {}
        status_dict["TIME"] = runtime

        self.UDP.write_reg_wib_checked(0x4, 0x8) #Internal clock is selected
        self.UDP.write_reg_wib_checked(0x12, 0x8000)
        self.UDP.write_reg_wib_checked(0x12, 0x100)
        time.sleep(0.02)

        #stat= self.UDP.read_reg_wib(32) #reg32 is for ProtoDUNE, reserved but not used
        #adc_errcnt =(stat&0x0FFFF0000) >> 16  
        #header_errcnt =(stat&0x0FFFF)   
        for i in range(5):
            link_status = self.UDP.read_reg_wib(0x21)
            eq_status   = self.UDP.read_reg_wib(0x24)
            time.sleep(0.001)

        status_dict["FEMB0_LINK"] = link_status&0xFF
        status_dict["FEMB0_EQ"  ] = eq_status&0x0F 
        status_dict["FEMB1_LINK"] = (link_status&0xFF00)>>8
        status_dict["FEMB1_EQ"  ] = (eq_status&0xF0)>>4 
        status_dict["FEMB2_LINK"] = (link_status&0xFF0000)>>16
        status_dict["FEMB2_EQ"  ] = (eq_status&0xF00)>>8 
        status_dict["FEMB3_LINK"] = (link_status&0xFF000000)>>24
        status_dict["FEMB3_EQ"  ] = (eq_status&0xF000)>>12 
                       
        self.UDP.write_reg_wib_checked(0x12, 0x000)
        for i in range(4):
            for j in range(4):
                self.UDP.write_reg_wib_checked(0x12, (i<<2) + j)
                reg34 = self.UDP.read_reg_wib(0x22)
                femb_ts_cnt = (reg34&0xFFFF0000)>>16
                chkerr_cnt = (reg34&0xFFFF)
                reg35 = self.UDP.read_reg_wib(0x25)
                frameerr_cnt =(reg35&0xFFFF) 
                status_dict["FEMB%d_TS_LINK%d"%(i, j)       ] = femb_ts_cnt 
                status_dict["FEMB%d_CHK_ERR_LINK%d"%(i, j)  ] = chkerr_cnt 
                status_dict["FEMB%d_FRAME_ERR_LINK%d"%(i, j)] = frameerr_cnt 

        for j in range(3):
            for k in range(5):
                self.UDP.write_reg_wib_checked(5, 0x00000)
                self.UDP.write_reg_wib_checked(5, 0x00000 | 0x10000)
                time.sleep(0.01)
                self.UDP.write_reg_wib_checked(5, 0x00000)
            vcts =[]
            for i in range(35):
                self.UDP.write_reg_wib_checked(5, i)
                time.sleep(0.001)
                tmp = self.UDP.read_reg_wib(6) & 0xFFFFFFFF
                if ( (tmp&0x40000000)>>16 == 0x4000 ):
                    tmp = tmp & 0x3fff
                if (tmp&0x3f00 == 0x3f00):
                    tmp = tmp & 0x3fff0000
                vcts.append(tmp)
                time.sleep(0.001)

        wib_vcc   = (((vcts[0x19]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001  + 2.5
        wib_t     = (((vcts[0x19]&0x0FFFF) & 0x3FFF) * 62.5) * 0.001 
        wib_vbias = (((vcts[0x1A]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
        wib_ibias = ((vcts[0x1A]& 0x3FFF) * 19.075) * 0.000001 / 0.1
        wib_v18   = (((vcts[0x1B]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
        wib_i18   = ((vcts[0x1B]& 0x3FFF) * 19.075) * 0.000001 / 0.01
        wib_v36   = (((vcts[0x1C]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
        wib_i36   = ((vcts[0x1C]& 0x3FFF) * 19.075) * 0.000001 / 0.01
        wib_v28   = (((vcts[0x1D]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
        wib_i28   = ((vcts[0x1D]& 0x3FFF) * 19.075) * 0.000001 / 0.01
        status_dict["WIB_2991_VCC"] = wib_vcc 
        status_dict["WIB_2991_T"] = wib_t 
        status_dict["WIB_BIAS_V"] = wib_vbias 
        status_dict["WIB_BIAS_I"] = wib_ibias 
        status_dict["WIB_V18_V"]  = wib_v18 
        status_dict["WIB_V18_I"]  = wib_i18 
        status_dict["WIB_V36_V"]  = wib_v36 
        status_dict["WIB_V36_I"]  = wib_i36 
        status_dict["WIB_V28_V"]  = wib_v28 
        status_dict["WIB_V28_I"]  = wib_i28 
        bias_vcc  = (((vcts[0x00]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001  + 2.5
        bias_t    = (((vcts[0x00]&0x0FFFF) & 0x3FFF) * 62.5) * 0.001
        status_dict["BIAS_2991_V"]  = bias_vcc 
        status_dict["BIAS_2991_T"]  = bias_t 
        status_dict["WIB_PC"] = status_dict["WIB_BIAS_V"] * status_dict["WIB_BIAS_I"] + \
                                status_dict["WIB_V18_V"] * status_dict["WIB_V18_I"] + \
                                status_dict["WIB_V36_V"] * status_dict["WIB_V36_I"] + \
                                status_dict["WIB_V28_V"] * status_dict["WIB_V28_I"]  

        for fembno in range(4):
            vct = []
            vcs = []
            vs  = []
            cs  = []

            femb_vcts=vcts[fembno*6+1: fembno*6+7]
            vct = np.array(femb_vcts)
            vc25 = vcts[31+fembno]
            status_dict["FEMB%d_2991_VCC"%fembno] = (((vct[0]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001 + 2.5
            status_dict["FEMB%d_2991_T"%fembno  ]   = (((vct[0]&0x0FFFF) & 0x3FFF) * 62.5) * 0.001
            status_dict["FEMB%d_FMV39_V"%fembno] = (((vct[1]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
            status_dict["FEMB%d_FMV39_I"%fembno] = ((vct[1]& 0x3FFF) * 19.075) * 0.000001 / 0.1
            status_dict["FEMB%d_FMV30_V"%fembno] = (((vct[2]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
            status_dict["FEMB%d_FMV30_I"%fembno] = ((vct[2]& 0x3FFF) * 19.075) * 0.000001 / 0.1
            status_dict["FEMB%d_FMV18_V"%fembno] = (((vct[4]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
            status_dict["FEMB%d_FMV18_I"%fembno] = ((vct[4]& 0x3FFF) * 19.075) * 0.000001 / 0.1
            status_dict["FEMB%d_AMV33_V"%fembno] = (((vct[3]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
            status_dict["FEMB%d_AMV33_I"%fembno] = ((vct[3]& 0x3FFF) * 19.075) * 0.000001 / 0.01
            status_dict["FEMB%d_BIAS_V"%fembno ]  = (((vct[5]&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
            status_dict["FEMB%d_BIAS_I"%fembno ]  = ((vct[5]& 0x3FFF) * 19.075) * 0.000001 / 0.1
            #status_dict["FEMB%d_AMV28_V"%fembno] = (((vc25&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
            #status_dict["FEMB%d_AMV28_I"%fembno] = ((vc25& 0x3FFF) * 19.075) * 0.000001 / 0.01
            #status_dict["FEMB%d_AMV33_I"%fembno] -= status_dict["FEMB%d_AMV28_I"%fembno]
            status_dict["FEMB%d_PC"%fembno] =   status_dict["FEMB%d_FMV39_V"%fembno] * status_dict["FEMB%d_FMV39_I"%fembno] + \
                                                status_dict["FEMB%d_FMV30_V"%fembno] * status_dict["FEMB%d_FMV30_I"%fembno] + \
                                                status_dict["FEMB%d_FMV18_V"%fembno] * status_dict["FEMB%d_FMV18_I"%fembno] + \
                                                status_dict["FEMB%d_AMV33_V"%fembno] * status_dict["FEMB%d_AMV33_I"%fembno] + \
                                                status_dict["FEMB%d_BIAS_V"%fembno ] * status_dict["FEMB%d_BIAS_I"%fembno ] 
                                                #status_dict["FEMB%d_BIAS_V"%fembno ] * status_dict["FEMB%d_BIAS_I"%fembno ] + \
                                                #status_dict["FEMB%d_AMV28_V"%fembno] * status_dict["FEMB%d_AMV28_I"%fembno] 
        return status_dict


    def FEMBs_SCAN(self):
        print ("Finding available FEMBs starts...")
        self.err_code = "" 
        for wib_ip in self.WIB_IPs:
            self.FEMB_DECTECT(wib_ip)
        if len(self.act_fembs) == 0:
            print ("No FEMB is availabe, please double check! Exit Anyway!")
            sys.exit()
        else:
            print ("FEMB scanning is done" )


    def WIBs_CFG_INIT(self):
        for wib_ip in list(self.act_fembs.keys()):
            self.UDP.UDP_IP = wib_ip
            self.WIB_UDP_CTL( wib_ip, WIB_UDP_EN = False) #disable Highspeed data
            if (self.jumbo_flag):
                self.UDP.write_reg_wib_checked(0x1F, 0xEFB) #normal operation
            else:
                self.UDP.write_reg_wib_checked(0x1F, 0x1FB) #normal operation
            self.UDP.write_reg_wib_checked(0x0F, 0x0) #normal operation
            self.WIB_CLKCMD_cs(wib_ip )# choose clock source
            femb_sws = [0, 0, 0, 0]
            for femb_addr in range(4):
                if self.act_fembs[wib_ip][femb_addr] == True:
                    femb_sws[femb_addr] = 1
            self.WIB_PWR_FEMB(wib_ip, femb_sws)

    def FEMBs_CE_OFF(self):
        for wib_ip in list(self.act_fembs.keys()):
            self.UDP.UDP_IP = wib_ip
            self.WIB_PWR_FEMB(wib_ip, [0, 0, 0, 0])

    def WIB_PLL_wr(self, wib_ip, addr, din):
        self.UDP.UDP_IP = wib_ip
        value = 0x01 + ((addr&0xFF)<<8) + ((din&0x00FF)<<16)
        self.UDP.write_reg_wib_checked (11,value)
        time.sleep(0.01)
        self.UDP.write_reg_wib_checked (10,1)
        time.sleep(0.01)
        self.UDP.write_reg_wib_checked (10,0)
        time.sleep(0.02)

    def WIB_PLL_cfg(self, wib_ip ):
        with open(self.pllfile,"r") as f:
            line = f.readline()
            adrs_h = []
            adrs_l = []
            datass = []
            cnt = 0
            while line:
                cnt = cnt + 1
                line = f.readline()
                tmp = line.find(",")
                if tmp > 0:
                    adr = int(line[2:tmp],16)
                    adrs_h.append((adr&0xFF00)>>8)
                    adrs_l.append((adr&0xFF))
                    datass.append((int(line[tmp+3:-2],16))&0xFF)
        self.UDP.UDP_IP = wib_ip
        lol_flg = False
        for i in range(5):
            print ("check PLL status, please wait...")
            time.sleep(1)
            ver_value = self.UDP.read_reg_wib (12)
            ver_value = self.UDP.read_reg_wib (12)
            lol = (ver_value & 0x10000)>>16
            lolXAXB = (ver_value & 0x20000)>>17
            INTR = (ver_value & 0x40000)>>18
            if (lol == 1):
                lol_flg = True
                break
        if (lol_flg):
            print ("PLL of WIB (%s) has locked"%wib_ip)
            print ("Select system clock and CMD from MBB")
            self.UDP.write_reg_wib_checked (4, 0x03)

        else:
            print ("configurate PLL of WIB (%s), please wait..."%wib_ip)
            p_addr = 1
            #step1
            page4 = adrs_h[0]
            self.WIB_PLL_wr( wib_ip, p_addr, page4)
            self.WIB_PLL_wr( wib_ip, adrs_l[0], datass[0])
            #step2
            page4 = adrs_h[1]
            self.WIB_PLL_wr( wib_ip, p_addr, page4)
            self.WIB_PLL_wr( wib_ip, adrs_l[1], datass[1])
            #step3
            page4 = adrs_h[2]
            self.WIB_PLL_wr( wib_ip, p_addr, page4)
            self.WIB_PLL_wr( wib_ip, adrs_l[2], datass[2])
            time.sleep(0.5)
            #step4
            for cnt in range(len(adrs_h)):
                if (page4 == adrs_h[cnt]):
                    tmpadr = adrs_l[2]
                    self.WIB_PLL_wr(wib_ip, adrs_l[cnt], datass[cnt])
                else:
                    page4 = adrs_h[cnt]
                    self.WIB_PLL_wr( wib_ip, p_addr, page4)
                    self.WIB_PLL_wr(wib_ip, adrs_l[cnt], datass[cnt])
            for i in range(10):
                time.sleep(3)
                print ("check PLL status, please wait...")
                self.UDP.UDP_IP = wib_ip
                ver_value = self.UDP.read_reg_wib (12)
                ver_value = self.UDP.read_reg_wib (12)
                lol = (ver_value & 0x10000)>>16
                lolXAXB = (ver_value & 0x20000)>>17
                INTR = (ver_value & 0x40000)>>18
                if (lol == 1):
                    print ("PLL of WIB(%s) is locked"%wib_ip)
                    self.UDP.write_reg_wib_checked (4, 0x03)
                    break
                if (i ==9):
                    print ("Fail to configurate PLL of WIB(%s), please check if MBB is on or 16MHz from dAQ"%wib_ip)
                    print ("Exit anyway")
                    sys.exit()

    def WIB_CLKCMD_cs(self, wib_ip ):
        self.UDP.UDP_IP = wib_ip
        if (self.Int_CLK ):
            self.UDP.write_reg_wib_checked(0x04, 0x08) #select WIB onboard system clock and CMD
        else:
            self.WIB_PLL_cfg(wib_ip ) #select system clock and CMD from MBB


    def CE_CHK_CFG(self, \
                   pls_cs=0, dac_sel=0, fpgadac_en=0, asicdac_en=0, fpgadac_v=0, \
                   pls_gap = 500, pls_dly = 10, mon_cs=0, \
                   data_cs = 0, \
                   sts=0, snc=0, sg0=0, sg1=1, st0=1, st1=1, smn=0, sdf=1, \
                   slk0 = 0, stb1 = 0, stb = 0, s16=0, slk1=0, sdc=0, swdac1=0, swdac2=0, dac=0, \
                  ):
        cfglog = []
        if (mon_cs == 0):
            tp_sel = ((asicdac_en&0x01) <<1) + (fpgadac_en&0x01) + ((dac_sel&0x1)<<8)
        else:
            tp_sel = 0x402

        if (pls_cs == 0 ):
            pls_cs_value = 0x3 #disable all
        elif (pls_cs == 1 ): #internal pls
            pls_cs_value = 0x2 
        elif (pls_cs == 2 ): #external pls
            pls_cs_value = 0x1 
        elif (pls_cs == 3 ): #enable int and ext pls
            pls_cs_value = 0x0 

        if (fpgadac_en == 1):
            reg_5_value = ((pls_gap<<16)&0xFFFF0000) + ((pls_dly<<8)&0xFF00) + ( fpgadac_v& 0xFF )
        else:
            reg_5_value = ((pls_gap<<16)&0xFFFF0000) + ((pls_dly<<8)&0xFF00) + ( 0x00 )

        for wib_ip in list(self.act_fembs.keys()):
            for femb_addr in range(4):
                if self.act_fembs[wib_ip][femb_addr] == True:
                    self.UDP.UDP_IP = wib_ip
                    self.UDP.write_reg_femb(femb_addr,  0, 1)
                    time.sleep(0.001)
                    self.UDP.write_reg_femb_checked (femb_addr,  5, reg_5_value)
                    self.UDP.write_reg_femb_checked (femb_addr, 16, tp_sel&0x0000ffff)
                    self.UDP.write_reg_femb_checked (femb_addr, 18, pls_cs_value)
                    if ( data_cs&0x0F != 0):
                        self.UDP.write_reg_femb_checked (femb_addr, 42, ((femb_addr&0x0F)<<4) + (data_cs&0x0F))
                    else:
                        self.UDP.write_reg_femb_checked (femb_addr, 42, 0)

                    #FE configuration
                    if (self.fecfg_loadflg ):
                        regs = self.REGS
                    else:
                        self.FEREG_MAP.set_fe_board(sts, snc, sg0, sg1, st0, st1, smn, sdf,\
                                                    slk0, stb1, stb, s16, slk1, sdc, swdac1, swdac2, dac)
                        regs = self.FEREG_MAP.REGS
                    fe_regs = [0x00000000]*(8+1)*4
                    for chip in [0,2,4,6]:
                        chip_bits_len = 8*(16+2)
                        chip_fe_regs0 = regs[   chip*chip_bits_len: (chip+1)* chip_bits_len]
                        chip_fe_regs1 = regs[   (chip+1)*chip_bits_len: (chip+2)* chip_bits_len]
                        chip_regs = []
                        for onebit in chip_fe_regs0:
                            chip_regs.append(onebit)
                        for onebit in chip_fe_regs1:
                            chip_regs.append(onebit)
                        len32 = len(chip_regs)//32
                        if (len32 != 9):
                            print ("ERROR FE register mapping")
                        else:
                            for i in range(len32):
                                if ( i*32 <= len(chip_regs) ):
                                    bits32 = chip_regs[i*32: (i+1)*32]
                                    fe_regs[int(chip/2*len32) + i ] = (sum(v<<j for j, v in enumerate(bits32)))
                    i = 0
                    for regNum in range(0x200,0x200+len(fe_regs),1):
                        self.UDP.write_reg_femb_checked (femb_addr, regNum, fe_regs[i])
                        i = i + 1
                    self.UDP.write_reg_femb (femb_addr, 2, 1) #SPI write
                    time.sleep(0.001)
                    self.UDP.write_reg_femb (femb_addr, 2, 1) #SPI write
                    time.sleep(0.001)
                    self.UDP.write_reg_femb (femb_addr, 2, 1) #SPI write
                    time.sleep(0.001)
                    fe_rb_regs = []
                    for regNum in range(0x250,0x250+len(fe_regs),1):
                        val = self.UDP.read_reg_femb (femb_addr, regNum ) 
                        fe_rb_regs.append( val )
                    j = 0
                    for j in range(len(fe_regs)):
                        if (fe_regs[j] != fe_rb_regs[j]) and (data_cs == 0 ):
                            print ("%dth, %8x,%8x"%(j, fe_regs[j],fe_rb_regs[j]))
                            fid = "IP%s-SLOT%d"%(wib_ip, femb_addr)
                            if ( j<= 9 ):
                                print ("FE-ADC 0 SPI failed")
                                spi_err ="-F8_FE01"
                            elif ( j<= 18 ):
                                print ("FE-ADC 1 SPI failed")
                                spi_err ="-F8_FE23"
                            elif ( j<= 27 ):
                                print ("FE-ADC 2 SPI failed")
                                spi_err ="-F8_FE34"
                            elif ( j<= 36 ):
                                print ("FE-ADC 3 SPI failed")
                                spi_err ="-F8_FE56"
                            elif ( j<= 45 ):
                                print ("FE-ADC 4 SPI failed")
                                spi_err ="-F8_IDLE0"
                            elif ( j<= 54 ):
                                print ("FE-ADC 5 SPI failed")
                                spi_err ="-F8_IDLE1"
                            elif ( j<= 64 ):
                                print ("FE-ADC 6 SPI failed")
                                spi_err ="-F8_IDLE2"
                            elif ( j<= 72 ):
                                print ("FE-ADC 7 SPI failed")
                                spi_err ="-F8_IDLE3"
                            else:
                                spi_err =""
                            if  fid in self.err_code:  
                                t = self.err_code.index (fid) + len(fid)
                                self.err_code = self.err_code[0:t] + spi_err + self.err_code[t:]
                    #enable data stream to WIB and reset transceiver
                    self.UDP.write_reg_femb_checked (femb_addr, 9, 9)

                    bl_mean = 0
                    bl_rms = 0
                    if (self.fe_monflg):
                        bl = []
                        for i in range(10):
                            adc_v = self.FEMB_MON(femb_addr = femb_addr)
                            bl.append(adc_v )
                        bl.remove(max(bl))
                        bl.remove(min(bl))
                        bl_mean=int(np.mean(bl))
                        bl_rms=np.std(bl)

                    cfglog.append( [ wib_ip, femb_addr,\
                           self.act_fembs[wib_ip][femb_addr], self.fecfg_loadflg, \
                           pls_cs, dac_sel, fpgadac_en, asicdac_en, fpgadac_v, \
                           pls_gap, pls_dly, mon_cs, \
                           data_cs, \
                           sts, snc, sg0, sg1, st0, st1, smn, sdf, \
                           slk0, stb1, stb, s16, slk1, sdc, swdac1, swdac2, dac, \
                           bl_mean, bl_rms ] )
        return cfglog

    def FEMB_MON(self,femb_addr=0):
        self.UDP.write_reg_wib (38, 0)
        self.UDP.write_reg_wib (38, 1)
        self.UDP.write_reg_wib (38, 0)
        self.UDP.write_reg_wib (38, 1)
        self.UDP.write_reg_wib (38, 0)
        self.UDP.write_reg_wib (38, 1)
        self.UDP.write_reg_wib (38, 0)
        rinc = int (femb_addr // 2)
        rloc =  int (femb_addr % 2)
        tmp = self.UDP.read_reg_wib (38+rinc)
        mondac_v = (tmp&0x0000FFFF) if rloc == 1 else ((tmp>>16)&0x0000FFFF)
        return mondac_v

 
    def FEMB_ASIC_CS(self,wib_ip, femb_addr=0, asic=0):
        self.UDP.UDP_IP = wib_ip
        femb_asic = asic & 0x0F
        wib_asic =  ( ((femb_addr << 16)&0x000F0000) + ((femb_asic << 8) &0xFF00) )
        self.UDP.write_reg_wib_checked ( 7, wib_asic | 0x80000000)
        self.UDP.write_reg_wib_checked ( 7, wib_asic)

    def TPC_UDPACQ(self, cfglog):
        tpc_data = []
        for wib_ip in list(self.act_fembs.keys()):
            tpc_data += self.WIB_UDPACQ( wib_ip, cfglog)
#        print (len(tpc_data))
        return tpc_data

    def WIB_UDPACQ(self, wib_ip, cfglog):
        d_wib = []
        for femb_addr in range(4):
            if self.act_fembs[wib_ip][femb_addr] == True:
                d_wib.append( self.FEMB_UDPACQ(wib_ip, femb_addr, cfglog) )
        return d_wib

    def FEMB_UDPACQ(self, wib_ip, femb_addr, cfglog):
        self.UDP.UDP_IP = wib_ip
        self.UDP.write_reg_wib_checked(0x01, 0x2) #Time Stamp Reset command encoded in 2MHz 
        self.UDP.write_reg_wib_checked(0x01, 0x0) 
        self.UDP.write_reg_wib_checked(18, 0x8000) #reset error counters
        if (self.DAQstream_en):
            self.UDP.write_reg_wib_checked(20, 0x03) #disable data stream and synchronize to Nevis
            self.UDP.write_reg_wib_checked(20, 0x00) #enable data stream to Nevis
        d_sts = []
        for i in range(self.sts_num):
            d_sts.append( self.WIB_STATUS(wib_ip) )
        self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = True) #Enable HS data from the WIB to PC through UDP
        if self.act_fembs[wib_ip][femb_addr] == True:
            print ("Take data from WIB%s FEMB%d"%(wib_ip, femb_addr))
            raw_asic = []
            for asic in range(8):
                self.FEMB_ASIC_CS(wib_ip, femb_addr, asic)
                raw_asic.append( self.UDP.get_rawdata_packets(self.val) )
            for cfg in cfglog:
                tmp = [cfg]
                if (cfg[0] == wib_ip) and (cfg[1] == femb_addr):
                    tmp += [raw_asic] + [d_sts]
                    if self.f_save :
                        fn = self.savedir + "/" + "WIB" + cfg[0].replace(".", "_") + "_FEMB%d"%cfg[1] + "_%d_%02d"%(cfg[3], cfg[12]) + \
                             "FE_%d%d%d%d%d%d%d%d%02d"%(cfg[13], cfg[14], cfg[15], cfg[16], cfg[17], cfg[18], cfg[27], cfg[28], cfg[29]) + ".bin"
                        with open(fn, "wb") as fp:
                            pickle.dump(tmp, fp)
                        tmp = None
                    break
        else:
            tmp = None
        self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False) #disable HS data from this WIB to PC through UDP
        return tmp

