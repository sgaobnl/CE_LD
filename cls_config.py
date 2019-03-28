# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 3/28/2019 10:16:31 AM
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

class CLS_CONFIG:
    def __init__(self):
        self.jumbo_flag = False 
        self.FEMB_ver = 0x501
        self.WIB_ver = 0x109
        self.WIB_IPs = ["192.168.121.1", "192.168.121.2", "192.168.121.3", \
                        "192.168.121.4", "192.168.121.5", "192.168.121.6",] #WIB IPs connected to host-PC
        self.MBB_IP  = "192.168.121.10"
        self.act_fembs = {}
        self.UDP = CLS_UDP()
        self.UDP.jumbo_flag = self.jumbo_flag

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
        self.WIB_IPs = active_wibs
        print ("WIB scanning is done" )

    def WIB_PWR_FEMB(self, wib_ip, femb_sws=[1,1,1,1]):
        print ("FEMBs power operation on the WIB with IP = %s, wait a moment"%wib_ip)
        self.UDP.UDP_IP = wib_ip
        pwr_status = self.UDP.read_reg_wib (0x8)
        pwr_ctl = [0x31000F, 0x5200F0, 0x940F00, 0x118F000]
        for i in range(len(femb_sws)):
            if ( femb_sws[i] == 1):
                pwr_status |= np.uint32(pwr_ctl[i])
                self.UDP.write_reg_wib_checked (0x8, pwr_status )#FEMB0 ON
                time.sleep(1)
            else:
                pwr_status &= ~np.uint32(pwr_ctl[i])
                self.UDP.write_reg_wib_checked (0x8, pwr_status )#FEMB0 ON
                time.sleep(1)

    def FEMB_DECTECT(self, wib_ip):
        self.UDP.UDP_IP = wib_ip
        self.WIB_PWR_FEMB(wib_ip, femb_sws=[1,1,1,1])
        stats = self.WIB_STATUS(wib_ip)
        keys = list(stats.keys())
        fembs_found = [True, True, True, True]
        for i in range(4):
            for key in keys:
                if key in "FEMB%d_LINK"%i:
                    if (stats[key] != 0xFF):
                        print ("FEMB%d LINK is broken!"%i)
                        fembs_found[i] = False
                elif key in "FEMB%d_EQ"%i:
                    if (stats[key] != 0xF):
                        print ("FEMB%d EQ is broken!"%i)
                        fembs_found[i] = False
                elif key in "FEMB%d_BIAS_I"%i:
                    if (stats[key] < 0.001 ):
                        print ("FEMB%d BIAS current (%fA) is lower than expected"%(i, stats[key]) )
                        fembs_found[i] = False
                    elif (stats[key] > 0.1 ):
                        print ("FEMB%d BIAS current (%fA) is higer than expected"%(i, stats[key]) )
                        fembs_found[i] = False
                elif key in "FEMB%d_FMV39_I"%i:
                    if (stats[key] < 0.010 ):
                        print ("FEMB%d FM_V39 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                    elif (stats[key] > 0.2 ):
                        print ("FEMB%d FM_V39 current (%fA) is higer than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                elif key in "FEMB%d_FMV30_I"%i:
                    if (stats[key] < 0.050 ):
                        print ("FEMB%d FM_V30 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                    elif (stats[key] > 0.5 ):
                        print ("FEMB%d FM_V30 current (%fA) is higer than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                elif key in "FEMB%d_FMV18_I"%i:
                    if (stats[key] < 0.250 ):
                        print ("FEMB%d FM_V30 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                    elif (stats[key] > 1.0 ):
                        print ("FEMB%d FM_V30 current (%fA) is higer than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                elif key in "FEMB%d_AMV33_I"%i:
                    if (stats[key] < 0.100 ):
                        print ("FEMB%d AM_V33 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                    elif (stats[key] > 1.0 ):
                        print ("FEMB%d AM_V33 current (%fA) is higer than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                elif key in "FEMB%d_AMV28_I"%i:
                    if (stats[key] < 0.100 ):
                        print ("FEMB%d AM_V28 current (%fA) is lower than expected"%(i, stats[key] ))
                        fembs_found[i] = False
                    elif (stats[key] > 1.0 ):
                        print ("FEMB%d AM_V28 current (%fA) is higer than expected"%(i, stats[key] ))
                        fembs_found[i] = False
            if (fembs_found[i]): #Link and current are good
                self.UDP.write_reg_femb(i, 0x0, 0x0)
                self.UDP.read_reg_femb(i, 0x102)
                ver_value = self.UDP.read_reg_femb(i, 0x101)
                if (ver_value > 0 ):
                    if (ver_value&0xFFFF != self.FEMB_ver):
                        print ("FEMB%d FE version is %x, which is different from default (%x)!"%(i, ver_value, self.FEMB_ver))
                        fembs_found[i] = False
                elif (ver_value <= 0 ):
                        print ("I2C of FEMB%d is broken"%i)
                        fembs_found[i] = False
        self.act_fembs[wib_ip] = fembs_found
        print self.act_fembs 

    def WIB_STATUS(self, wib_ip):
        runtime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        self.UDP.UDP_IP = wib_ip
        status_dict = {}
        self.UDP.write_reg_wib(0x4, 0x8) #Internal clock is selected
        self.UDP.write_reg_wib(0x12, 0x8000)
        self.UDP.write_reg_wib(0x12, 0x100)
        #stat= self.UDP.read_reg_wib(32) #reg32 is for ProtoDUNE, reserved but not used
        #adc_errcnt =(stat&0x0FFFF0000) >> 16  
        #header_errcnt =(stat&0x0FFFF)   
        link_status = self.UDP.read_reg_wib(0x21)
        eq_status   = self.UDP.read_reg_wib(0x24)

        status_dict["FEMB0_LINK"] = link_status&0xFF
        status_dict["FEMB0_EQ"  ] = eq_status&0x0F 
        status_dict["FEMB1_LINK"] = (link_status&0xFF00)>>8
        status_dict["FEMB1_EQ"  ] = (eq_status&0xF0)>>4 
        status_dict["FEMB2_LINK"] = (link_status&0xFF0000)>>16
        status_dict["FEMB2_EQ"  ] = (eq_status&0xF00)>>8 
        status_dict["FEMB3_LINK"] = (link_status&0xFF000000)>>24
        status_dict["FEMB3_EQ"  ] = (eq_status&0xF000)>>12 
                       
        self.UDP.write_reg_wib(0x12, 0x000)
        for i in range(4):
            for j in range(4)
                self.UDP.write_reg_wib_checked(0x12, (i<<2) + j)
                reg34 = self.UDP.read_reg_wib(0x22)
                femb_ts_cnt = (reg34&0xFFFF0000)>>16
                chkerr_cnt = (reg34&0xFFFF)
                reg35 = self.UDP.read_reg_wib(0x25)
                frameerr_cnt =(reg35&0xFFFF) 

                status_dict["FEMB%d_TS_LINK%d"%(i, j)         ] = femb_ts_cnt 
                status_dict["FEMB%d_CHK_ERR_LINK%d"%(i, j)    ] = chkerr_cnt 
                status_dict["FEMB%d_FRAME_ERR_LINK%d"%(i, j)  ] = frameerr_cnt 

        for j in range(3):
            self.UDP.write_reg_wib_checked(5, 0x00000)
            self.UDP.write_reg_wib_checked(5, 0x00000 | 0x10000)
            self.UDP.write_reg_wib_checked(5, 0x00000)
            time.sleep(0.1)
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
            status_dict["FEMB%d_AMV28_V"%fembno] = (((vc25&0x0FFFF0000) >> 16) & 0x3FFF) * 305.18 * 0.000001
            status_dict["FEMB%d_AMV28_I"%fembno] = ((vc25& 0x3FFF) * 19.075) * 0.000001 / 0.01
            status_dict["FEMB%d_AMV33_I"%fembno] -= status_dict["FEMB%d_AMV28_I"%fembno]
            status_dict["FEMB%d_PC"%fembno] =   status_dict["FEMB%d_FMV39_V"%fembno] * status_dict["FEMB%d_FMV39_I"%fembno] + \
                                                status_dict["FEMB%d_FMV30_V"%fembno] * status_dict["FEMB%d_FMV30_I"%fembno] + \
                                                status_dict["FEMB%d_FMV18_V"%fembno] * status_dict["FEMB%d_FMV18_I"%fembno] + \
                                                status_dict["FEMB%d_AMV33_V"%fembno] * status_dict["FEMB%d_AMV33_I"%fembno] + \
                                                status_dict["FEMB%d_BIAS_V"%fembno ] * status_dict["FEMB%d_BIAS_I"%fembno ] + \
                                                status_dict["FEMB%d_AMV28_V"%fembno] * status_dict["FEMB%d_AMV28_I"%fembno] 
        return status_dict

    def FEMBs_SCAN(self):
        print ("Finding available FEMBs starts...")
        for wib_ip in self.WIB_IPs:
            self.FEMB_DECTECT(wib_ip)


a = CLS_CONFIG()
a.WIBs_SCAN()
a.FEMBs_SCAN()

#        print ( status_dict["FEMB1_2991_T"] )
#        print ( status_dict["FEMB1_BIAS_V"] , status_dict["FEMB1_BIAS_I"]  )
#        print ( status_dict["FEMB1_FMV39_V"], status_dict["FEMB1_FMV39_I"] )
#        print ( status_dict["FEMB1_FMV30_V"], status_dict["FEMB1_FMV30_I"] )
#        print ( status_dict["FEMB1_FMV18_V"], status_dict["FEMB1_FMV18_I"] )
#        print ( status_dict["FEMB1_AMV33_V"], status_dict["FEMB1_AMV33_I"] )
#        print ( status_dict["FEMB1_AMV28_V"], status_dict["FEMB1_AMV28_I"] )

#            vcs = np.append(vct[1:6], vc25) 
#            vcsh = (vcs&0x0FFFF0000) >> 16 
#            vcshx = vcsh & 0x4000
#            for i in range(len(vcsh)):
#                if (vcshx[i] == 0 ):
#                    vs.append(vcsh[i])
#                else:
#                    vs.append(0)
#            vs = ((np.array(vs) & 0x3FFF) * 305.18) * 0.000001
# 
#            status_dict["BIAS_2991_V"]  = bias_vcc 
#
#            vcsl = (vcs&0x0FFFF) 
#            cs = ((vcsl & 0x3FFF) * 19.075) * 0.000001 / 0.1
#            cs[2] = cs[2] / 0.1
#            cs[5] = cs[5] / 0.1
#            cs_tmp =[]
#            for csi in cs:
#                if csi < 3.1 :
#                    cs_tmp.append(csi)
#                else:
#                    cs_tmp.append(0)
#            cs = np.array(cs_tmp)
#

#            monlogs.append ( mon_pre + "LINK/LINK_READ" + " " + str( (wib_link >> (8*fembno))&0xFF ) )
#            monlogs.append ( mon_pre + "EQER/EQER_READ" + " " + str((wib_eq >> (4*fembno))&0xF ) )
            #print (  "TEMP/TEMP_READ" + " " + "%3.3f"%temp )
            #print (  "BS50/VOLT_READ" + " " + "%3.3f"%vs[4] ) 
            #print (  "FM42/VOLT_READ" + " " + "%3.3f"%vs[0] ) 
            #print (  "FM30/VOLT_READ" + " " + "%3.3f"%vs[1] ) 
            #print (  "FM15/VOLT_READ" + " " + "%3.3f"%vs[3] ) 
            #print (  "AM36/VOLT_READ" + " " + "%3.3f"%vs[2] ) 
            #print (  "AM25/VOLT_READ" + " " + "%3.3f"%vs[5] ) 
            #print (  "BS50/CURR_READ" + " " + "%3.3f"%cs[4] ) 
            #print (  "FM42/CURR_READ" + " " + "%3.3f"%cs[0] ) 
            #print (  "FM30/CURR_READ" + " " + "%3.3f"%cs[1] ) 
            #print (  "FM15/CURR_READ" + " " + "%3.3f"%cs[3] ) 
            #print (  "AM36/CURR_READ" + " " + "%3.3f"%cs[2] ) 
            #print (  "AM25/CURR_READ" + " " + "%3.3f"%cs[5] ) 


    #def WIB_PWR_CTRL(self, wib_ip,  sw=True):


#    def FEMBs_SCAN(self, femb_verid=0x501):
#        print ("Finding available FEMBs starts...")
#        for wib_ip in self.WIB_IPs:
#            self.UDP.UDP_IP = wib_ip
#            self.UDP.jumbo_flag = self.jumbo_flag
#
#            self.UDP.write_reg_wib_checked (0x8, 0x1FFFFFF )#FEMB0&1&2&3 ON
#            time.sleep(3)
#            #
#
#
#        active_wibs = []
#        for wib_ip in self.WIB_IPs:
#            self.UDP.UDP_IP = wib_ip
#            self.UDP.jumbo_flag = self.jumbo_flag
#            for i in range(5):
#                wib_ver_rb = self.UDP.read_reg_wib (0xFF)
#                wib_ver_rb = self.UDP.read_reg_wib (0xFF)
#                if ((wib_ver_rb&0x0FFF) == wib_verid) and ( wib_ver_rb >= 0):
#                    print ("WIB with IP = %s is found"%wib_ip) 
#                    active_wibs.append(wib_ip)
#                    break
#                elif ( wib_ver_rb == -2):
#                    print ("Timeout. WIB with IP = %s isn't mounted, mask this IP"%wib_ip) 
#                    break
#                time.sleep(0.1)
#                if (i == 4):
#                    print ("WIB with IP = %s get error (code %d from CLS_UDP.read_reg()), mask this IP"%(wib_ip, wib_ver_rb)) 
#        self.WIB_IPs = active_wibs
#        print ("WIB scanning is done" )

#a.WIBs_SCAN()
#a.WIB_PWR_FEMB("192.168.121.1", femb_sws=[0,0,0,0])
#a.WIB_PWR_FEMB("192.168.121.1", femb_sws=[1,1,1,1])
#a.WIB_STATUS("192.168.121.1")
#a.FEMB_DECTECT("192.168.121.2")
#a.WIB_PWR_FEMB("192.168.121.2", femb_sws=[1,1,1,1])
#a.WIB_STATUS("192.168.121.2")
#a.WIBs_SCAN()
#for wib_ip in a.WIB_IPs:
#    a.FEMB_DECTECT(wib_ip)
#print a.act_fembs

#
#    def Init_CHK(self, wib_ip, femb_loc, wib_verid=0x109, femb_ver=0x501):
#        self.UDP.UDP_IP = wib_ip
#        self.UDP.jumbo_flag = self.jumbo_flag
#
#        wib_ver_rb = self.UDP.read_reg_wib (0xFF)
#        wib_ver_rb = self.UDP.read_reg_wib (0xFF)
#        if ((wib_ver_rb&0x0FFF) == wib_verid) and ( wib_ver_rb!= -1) :
#            print ("WIB with IP = %s is chosen"%wib_ip) 
#            pass
#
#        if (self.jumbo_flag):
#            jumbo_size = 0xEFB
#        else:
#            jumbo_size = 0x1FB
#        self.UDP.write_reg_wib_checked (0x1F, jumbo_size)
#        self.UDP.write_reg_wib_checked (0x10, 0x7F00)
#        self.UDP.write_reg_wib_checked (0x0F, 0x0)
#
#            #set normal mode
#            self.femb_meas.femb_config.femb.write_reg_wib_checked (16, 0x7F00)
#            self.femb_meas.femb_config.femb.write_reg_wib_checked (15, 0)
#            #self.femb_meas.femb_config.femb.write_reg_wib_checked (40, 0)
#            #self.femb_meas.femb_config.femb.write_reg_wib_checked (41, 0)
#            self.WIB_UDP_CTL(wib_ip, WIB_UDP_EN = False)
#
#
#        if ((wib_ver_rb&0x0FFF) == wib_verid) and ( wib_ver_rb!= -1) :
#
#    def WIB_CFG(self, wib_ip, femb_loc, ):
#    def FEMB_CFG(self, wib_ip, femb_loc,):
#    def FEMB_FEs_CFG(self, wib_ip, femb_loc, ):
#
#    def __init__(self):
#        self.UDP = CLS_UDP()
#        self.WIB_IPs = ["192.168.121.1", "192.168.121.2", "192.168.121.3", \
#                        "192.168.121.4", "192.168.121.5", "192.168.121.6",] #WIB IPs connected to host-PC
#        self.MBB_IP  = "192.168.121.10"
#
#
#
#
#        self.UDP_IP = "192.168.121.1"
#        self.U = False
#        self.jumbo_flag = True
#           
#            femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac, mon_cs = 0):
#
#    def config_femb_mode(self, femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac, mon_cs = 0):
#        if (mon_cs == 0):
#            tp_sel = ((asic_dac&0x01) <<1) + (fpga_dac&0x01) + ((dac_sel&0x1)<<8)
#        else:
#            #tp_sel = ((asic_dac&0x01) <<1) + (fpga_dac&0x01) + ((0x4)<<8)
#            tp_sel = 0x402
#
#        self.femb.write_reg_femb_checked (femb_addr, self.REG_EN_CALI, tp_sel&0x0000ffff)
#
#        self.femb.write_reg_femb_checked (femb_addr, 18, 0x11)
#        if (pls_cs == 0 ):
#            pls_cs_value = 0x3 #disable all
#        elif (pls_cs == 1 ): #internal pls
#            pls_cs_value = 0x2 
#        elif (pls_cs == 2 ): #external pls
#            pls_cs_value = 0x1 
#        elif (pls_cs == 3 ): #enable int and ext pls
#            pls_cs_value = 0x0 
#        self.femb.write_reg_femb_checked (femb_addr, 18, pls_cs_value)
#        print (femb_addr,  pls_cs, dac_sel, fpga_dac, asic_dac )
#        time.sleep(0.1)
#
#    def cots_adc_sft(self, femb_addr ):
#        self.default_set()
#        print ("COTS Shift and Phase Setting starts...")
##ADC for FE1
#        self.femb.write_reg_femb_checked (femb_addr, 21, self.fe1_sft )
#        self.femb.write_reg_femb_checked (femb_addr, 29, self.fe1_pha )
##ADC for FE2
#        self.femb.write_reg_femb_checked (femb_addr, 22, self.fe2_sft )
#        self.femb.write_reg_femb_checked (femb_addr, 30, self.fe2_pha )
##ADC for FE3
#        self.femb.write_reg_femb_checked (femb_addr, 23, self.fe3_sft )
#        self.femb.write_reg_femb_checked (femb_addr, 31, self.fe3_pha )
##ADC for FE4
#        self.femb.write_reg_femb_checked (femb_addr, 24, self.fe4_sft )
#        self.femb.write_reg_femb_checked (femb_addr, 32, self.fe4_pha )
##ADC for FE5
#        self.femb.write_reg_femb_checked (femb_addr, 25, self.fe5_sft )
#        self.femb.write_reg_femb_checked (femb_addr, 33, self.fe5_pha )
##ADC for FE6
#        self.femb.write_reg_femb_checked (femb_addr, 26, self.fe6_sft )
#        self.femb.write_reg_femb_checked (femb_addr, 34, self.fe6_pha )
##ADC for FE7
#        self.femb.write_reg_femb_checked (femb_addr, 27, self.fe7_sft )
#        self.femb.write_reg_femb_checked (femb_addr, 35, self.fe7_pha )
##ADC for FE8
#        self.femb.write_reg_femb_checked (femb_addr, 28, self.fe8_sft )
#        self.femb.write_reg_femb_checked (femb_addr, 36, self.fe8_pha )
#        self.femb.write_reg_femb (femb_addr, 8, 0 )
#        self.femb.write_reg_femb (femb_addr, 8, 0 )
#        time.sleep(0.02)
#        self.femb.write_reg_femb (femb_addr, 8, 0x10 )
#        self.femb.write_reg_femb (femb_addr, 8, 0x10 )
#        time.sleep(0.02)
#
#    def config_femb(self, femb_addr, fe_adc_regs, clk_cs, pls_cs, dac_sel, fpga_dac, asic_dac, mon_cs = 0):
#        #time stamp reset
#        self.femb.write_reg_femb (femb_addr, 0, 4)
#        self.femb.write_reg_femb (femb_addr, 0, 4)
#    
#        #sync time stamp /WIB
#        self.femb.write_reg_wib (1, 0)
#        self.femb.write_reg_wib (1, 0)
#        self.femb.write_reg_wib (1, 2)
#        self.femb.write_reg_wib (1, 2)
#        self.femb.write_reg_wib (1, 0)
#        self.femb.write_reg_wib (1, 0)
#    
#        #reset Error /WIB
#        self.femb.write_reg_wib (18, 0x8000)
#        self.femb.write_reg_wib (18, 0x8000)
#    
#        #RESET SPI
#        self.femb.write_reg_femb (femb_addr, self.REG_ASIC_RESET, 1)
#        self.femb.write_reg_femb (femb_addr, self.REG_ASIC_RESET, 1)
#        self.femb.write_reg_femb (femb_addr, self.REG_ASIC_RESET, 2)
#        self.femb.write_reg_femb (femb_addr, self.REG_ASIC_RESET, 2)
#        time.sleep(0.01)
#    
#        self.config_femb_mode(femb_addr, pls_cs, dac_sel, fpga_dac, asic_dac, mon_cs)
#        self.femb.write_reg_femb_checked (femb_addr, self.REG_TEST_PAT, self.REG_TEST_PAT_DATA)
#
#        #SPI write
#        self.cots_adc_sft( femb_addr )
#        time.sleep(0.01)
#        k = 0
#        while (k<2):
#            #disable FEMB stream data to WIB
#            self.femb.write_reg_femb_checked(femb_addr, 9, 0x0)
#            time.sleep(0.01)
#            i = 0
#            for regNum in range(self.REG_SPI_BASE,self.REG_SPI_BASE+len(fe_adc_regs),1):
#                self.femb.write_reg_femb_checked (femb_addr, regNum, fe_adc_regs[i])
#                i = i + 1
#    
#            time.sleep(0.01)
#            self.femb.write_reg_femb (femb_addr, self.REG_ASIC_SPIPROG, 1)
#    
#            if (k ==1):
#                j = 0
#                while (j < 10 ):
#                    time.sleep(0.01)
#                    fe_adc_rb_regs = []
#                    for regNum in range(self.REG_SPI_RDBACK_BASE,self.REG_SPI_RDBACK_BASE+len(fe_adc_regs),1):
#                        val = self.femb.read_reg_femb (femb_addr, regNum ) 
#                        fe_adc_rb_regs.append( val )
#                        time.sleep(0.001)
#    
#                    spi_err_flg = 0
#                    i = 0
#                    for i in range(len(fe_adc_regs)):
#                        if fe_adc_regs[i] != fe_adc_rb_regs[i]:
#                            spi_err_flg = 1
#                            print "%dth, %8x,%8x"%(i, fe_adc_regs[i],fe_adc_rb_regs[i])
#                            if ( i<= 9 ):
#                                print "FE-ADC 0 SPI failed"
#                                spi_err_flg = 0
#                            elif ( i<= 18 ):
#                                print "FE-ADC 1 SPI failed"
#                            elif ( i<= 27 ):
#                                print "FE-ADC 2 SPI failed"
#                            elif ( i<= 36 ):
#                                print "FE-ADC 3 SPI failed"
#                            elif ( i<= 45 ):
#                                print "FE-ADC 4 SPI failed"
#                            elif ( i<= 54 ):
#                                print "FE-ADC 5 SPI failed"
#                            elif ( i<= 64 ):
#                                print "FE-ADC 6 SPI failed"
#                            elif ( i<= 72 ):
#                                print "FE-ADC 7 SPI failed"
#                    if (spi_err_flg == 1 ):
#                        j = j + 1
#                    else:
#                        break
##                if ( j >= 10 ):
##                    print "SPI ERROR "
##                    sys.exit()
#            #enable FEMB stream data to WIB
#            self.femb.write_reg_femb_checked (femb_addr, 9, 9)
#            self.femb.write_reg_femb_checked (femb_addr, 9, 9)
#            time.sleep(0.1)
#    
#            self.femb.write_reg_wib (20, 3)
#            time.sleep(0.001)
#            self.femb.write_reg_wib (20, 3)
#            time.sleep(0.001)
#            self.femb.write_reg_wib (20, 3)
#            time.sleep(0.001)
#            self.femb.write_reg_wib (20, 0)
#            time.sleep(0.001)
#            self.femb.write_reg_wib (20, 0)
#            time.sleep(0.001)
#            self.femb.write_reg_wib (20, 0)
#            time.sleep(0.001)
#            k = k + 1
#    
#        time.sleep(0.2)
#
#    def selectasic_femb(self,femb_addr=0, asic=0):
#        self.femb.write_reg_wib ( 7, 0x80000000)
#        self.femb.write_reg_wib ( 7, 0x80000000)
#        femb_asic = asic & 0x0F
#        self.femb.write_reg_femb_checked ( femb_addr, self.REG_SEL_CH, femb_asic)
#        self.femb.write_reg_femb_checked ( femb_addr, self.REG_HS, 1)
#        wib_asic =  ( ((femb_addr << 16)&0x000F0000) + ((femb_asic << 8) &0xFF00) )
#        self.femb.write_reg_wib (  7, wib_asic | 0x80000000)
#        self.femb.write_reg_wib (  7, wib_asic | 0x80000000)
#        self.femb.write_reg_wib (  7, wib_asic)
#        self.femb.write_reg_wib (  7, wib_asic)
#        time.sleep(0.001)
#
#    def get_rawdata_femb(self, femb_addr=0, asic=0):
#        i = 0
#        while ( 1 ):
#            i = i + 1
#            self.selectasic_femb(femb_addr, asic)
#            data = self.femb.get_rawdata()
#            break
#        return data
#
#    def get_rawdata_packets_femb(self, femb_addr=0, asic=0, val = 100 ):
#        i = 0
#        #while ( i < val ):
#        self.selectasic_femb(femb_addr, asic)
#        data = self.femb.get_rawdata_packets(val)
#        return data
#
#    def default_set(self ):
#        if (self.COTSADC == True):
#            print "COTS AM in use"
#            self.fe1_sft =0x00000000 
#            self.fe2_sft =0x00000000 
#            self.fe3_sft =0x00000000 
#            self.fe4_sft =0x00000000 
#            self.fe5_sft =0x00000000 
#            self.fe6_sft =0x00000000  
#            self.fe7_sft =0x00000000 
#            self.fe8_sft =0x00000000 
#
#            if (self.phase_set == 0 )  :
#                self.fe1_pha =0x00000000 
#                self.fe2_pha =0x00000000 
#                self.fe3_pha =0x00000000 
#                self.fe4_pha =0x00000000 
#                self.fe5_pha =0x00000000 
#                self.fe6_pha =0x00000000 
#                self.fe7_pha =0x00000000 
#                self.fe8_pha =0x00000000 
#                print hex(self.fe1_pha)
#            elif (self.phase_set == 2 ): 
#                self.fe1_pha =0xAAAAAAAA 
#                self.fe2_pha =0xAAAAAAAA 
#                self.fe3_pha =0xAAAAAAAA 
#                self.fe4_pha =0xAAAAAAAA 
#                self.fe5_pha =0xAAAAAAAA 
#                self.fe6_pha =0xAAAAAAAA 
#                self.fe7_pha =0xAAAAAAAA 
#                self.fe8_pha =0xAAAAAAAA 
#                print hex(self.fe1_pha)
#            elif (self.phase_set == 1 ): 
#                self.fe1_pha =0x55555555 
#                self.fe2_pha =0x55555555 
#                self.fe3_pha =0x55555555 
#                self.fe4_pha =0x55555555 
#                self.fe5_pha =0x55555555 
#                self.fe6_pha =0x55555555 
#                self.fe7_pha =0x55555555 
#                self.fe8_pha =0x55555555 
#                print hex(self.fe1_pha)
#            elif (self.phase_set == 3 ) :
#                self.fe1_pha =0xFFFFFFFF 
#                self.fe2_pha =0xFFFFFFFF 
#                self.fe3_pha =0xFFFFFFFF 
#                self.fe4_pha =0xFFFFFFFF 
#                self.fe5_pha =0xFFFFFFFF 
#                self.fe6_pha =0xFFFFFFFF 
#                self.fe7_pha =0xFFFFFFFF 
#                self.fe8_pha =0xFFFFFFFF 
#                print hex(self.fe1_pha)
#
#            else:
#                print "phase value should be 0 to 3, exit anyway"
#                sys.exit()
#    
#        else:
#            self.REG_LATCHLOC1_4 = 4
#            self.REG_LATCHLOC1_4_data = 0x04040404
#            self.REG_LATCHLOC5_8 = 14
#            self.REG_LATCHLOC5_8_data = 0x04040404
#            self.REG_CLKPHASE0 = 6 
#            self.REG_CLKPHASE_data0 = 0x000000FF #LN
#            self.REG_CLKPHASE1 = 15 
#            self.REG_CLKPHASE_data1 = 0x000000FF #LN
#            #self.sync_chkflg =  False
#            self.sync_chkflg = True 
#            self.ADC_TESTPATTERN = [0x12, 0x345, 0x678, 0xf1f, 0xad, 0xc01, 0x234, 0x567, 0x89d, 0xeca, 0xff0, 0x123, 0x456, 0x789, 0xabc, 0xdef]
#    ####################external clokc timing
#            clk_period = 5 #ns
#            self.clk_dis = 0 #0 --> enable, 1 disable
#            self.d14_rst_oft  = 0   // clk_period   
#            self.d14_rst_wdt  = (45  // clk_period )    
#            self.d14_rst_inv  = 1  
#            self.d14_read_oft = 480 // clk_period    
#            self.d14_read_wdt = 20  // clk_period    
#            self.d14_read_inv = 1 
#            self.d14_idxm_oft = 230 // clk_period    
#            self.d14_idxm_wdt = 270 // clk_period    
#            self.d14_idxm_inv = 0 
#            self.d14_idxl_oft = 480 // clk_period    
#            self.d14_idxl_wdt = 20  // clk_period    
#            self.d14_idxl_inv = 0 
#            self.d14_idl0_oft = 50  // clk_period    
#            self.d14_idl0_wdt = (190 // clk_period ) -1   
#            self.d14_idl1_oft = 480 // clk_period
#            self.d14_idl1_wdt = 20  // clk_period    
#            self.d14_idl_inv  = 0      
#    
#            self.d58_rst_oft  = 0   // clk_period 
#            self.d58_rst_wdt  = (45  // clk_period ) 
#            self.d58_rst_inv  = 1  
#            self.d58_read_oft = 480 // clk_period 
#            self.d58_read_wdt = 20  // clk_period 
#            self.d58_read_inv = 1 
#            self.d58_idxm_oft = 230 // clk_period 
#            self.d58_idxm_wdt = 270 // clk_period 
#            self.d58_idxm_inv = 0 
#            self.d58_idxl_oft = 480 // clk_period 
#            self.d58_idxl_wdt = 20  // clk_period 
#            self.d58_idxl_inv = 0 
#            self.d58_idl0_oft = 50  // clk_period 
#            self.d58_idl0_wdt = (190 // clk_period ) -1
#            self.d58_idl1_oft = 480 // clk_period
#            self.d58_idl1_wdt = 20  // clk_period 
#            self.d58_idl_inv  = 0       
#    ####################external clokc phase for V323 firmware
#            print "femb_config.yp : FM firmware version = 323"
#            self.d14_read_step = 11
#            self.d14_read_ud   = 0
#            self.d14_idxm_step = 9
#            self.d14_idxm_ud   = 0
#            self.d14_idxl_step = 7
#            self.d14_idxl_ud   = 0
#            self.d14_idl0_step = 12 
#            self.d14_idl0_ud   = 0
#            self.d14_idl1_step = 10 
#            self.d14_idl1_ud   = 0
#            self.d14_phase_en  = 1
#    
#            self.d58_read_step = 0
#            self.d58_read_ud   = 0
#            self.d58_idxm_step = 5
#            self.d58_idxm_ud   = 0
#            self.d58_idxl_step = 4
#            self.d58_idxl_ud   = 1
#            self.d58_idl0_step = 3
#            self.d58_idl0_ud   = 0
#            self.d58_idl1_step = 4
#            self.d58_idl1_ud   = 0
#            self.d58_phase_en  = 1
#    
#    #####################external clokc phase for V320 firmware
#    #        print "femb_config.yp : FM firmware version = 320"
#    #        self.d14_read_step = 7
#    #        self.d14_read_ud   = 0
#    #        self.d14_idxm_step = 3
#    #        self.d14_idxm_ud   = 0
#    #        self.d14_idxl_step = 1
#    #        self.d14_idxl_ud   = 1
#    #        self.d14_idl0_step = 5
#    #        self.d14_idl0_ud   = 0
#    #        self.d14_idl1_step = 2
#    #        self.d14_idl1_ud   = 0
#    #        self.d14_phase_en  = 1
#    #
#    #        self.d58_read_step = 1
#    #        self.d58_read_ud   = 1
#    #        self.d58_idxm_step = 0
#    #        self.d58_idxm_ud   = 0
#    #        self.d58_idxl_step = 5
#    #        self.d58_idxl_ud   = 1
#    #        self.d58_idl0_step = 6
#    #        self.d58_idl0_ud   = 0
#    #        self.d58_idl1_step = 5
#    #        self.d58_idl1_ud   = 0
#    #        self.d58_phase_en  = 1
#    #
#    ####################external clokc phase for V319 firmware
#    #        print "femb_config.yp : FM firmware version = 319"
#    #        self.d14_read_step = 7
#    #        self.d14_read_ud   = 0
#    #        self.d14_idxm_step = 9
#    #        self.d14_idxm_ud   = 0
#    #        self.d14_idxl_step = 4
#    #        self.d14_idxl_ud   = 0
#    #        self.d14_idl0_step = 9
#    #        self.d14_idl0_ud   = 0
#    #        self.d14_idl1_step = 6
#    #        self.d14_idl1_ud   = 0
#    #        self.d14_phase_en  = 1
#    #
#    #        self.d58_read_step = 5
#    #        self.d58_read_ud   = 0
#    #        self.d58_idxm_step = 7
#    #        self.d58_idxm_ud   = 0
#    #        self.d58_idxl_step = 2
#    #        self.d58_idxl_ud   = 1
#    #        self.d58_idl0_step = 9
#    #        self.d58_idl0_ud   = 0
#    #        self.d58_idl1_step = 5
#    #        self.d58_idl1_ud   = 0
#    #        self.d58_phase_en  = 1
#
#    def __init__(self):
#        self.COTSADC = False
#        #declare board specific registers
#        self.jumbo_flag = True
#        self.REG_RESET = 0
#        self.REG_ASIC_RESET = 1
#        self.REG_ASIC_SPIPROG = 2
#        self.REG_TEST_PAT = 3
#        self.REG_TEST_PAT_DATA = 0x01230000
#        self.REG_SEL_ASIC = 7 
#        self.REG_SEL_CH = 7
#        self.REG_SPI_BASE = 0x200
#        self.REG_SPI_RDBACK_BASE =0x250
#        #self.REG_FESPI_BASE = 0x250
#        #self.REG_ADCSPI_BASE = 0x200
##        self.REG_FESPI_RDBACK_BASE = 0x278
##        self.REG_ADCSPI_RDBACK_BASE =0x228 
#        self.REG_HS = 17
#        self.REG_EN_CALI = 16
#
#        self.femb = FEMB_UDP()
#        self.femb.jumbo_flag = self.jumbo_flag
#        #initialize FEMB UDP object
##COTS ADC
#        self.phase_set = 0
#        self.fe1_sft =0x00000000 
#        self.fe1_pha =0x00000000 
#        self.fe2_sft =0x00000000 
#        self.fe2_pha =0x00000000 
#        self.fe3_sft =0x00000000 
#        self.fe3_pha =0x00000000 
#        self.fe4_sft =0x00000000 
#        self.fe4_pha =0x00000000 
#        self.fe5_sft =0x00000000 
#        self.fe5_pha =0x00000000 
#        self.fe6_sft =0x00000000 
#        self.fe6_pha =0x00000000 
#        self.fe7_sft =0x00000000 
#        self.fe7_pha =0x00000000 
#        self.fe8_sft =0x00000000 
#        self.fe8_pha =0x00000000 
#
##P1 ADC
#        self.REG_LATCHLOC1_4 = 4
#        self.REG_LATCHLOC1_4_data = 0x04040404
#        self.REG_LATCHLOC5_8 = 14
#        self.REG_LATCHLOC5_8_data = 0x04040404
#        self.REG_CLKPHASE0 = 6 
#        self.REG_CLKPHASE_data0 = 0x000000FF #LN
#        self.REG_CLKPHASE1 = 15 
#        self.REG_CLKPHASE_data1 = 0x000000FF #LN
#        #self.sync_chkflg =  False
#        self.sync_chkflg = True 
#        self.ADC_TESTPATTERN = [0x12, 0x345, 0x678, 0xf1f, 0xad, 0xc01, 0x234, 0x567, 0x89d, 0xeca, 0xff0, 0x123, 0x456, 0x789, 0xabc, 0xdef]
#####################external clokc timing
#        clk_period = 5 #ns
#        self.clk_dis = 0 #0 --> enable, 1 disable
#        self.d14_rst_oft  = 0   // clk_period   
#        self.d14_rst_wdt  = (45  // clk_period )    
#        self.d14_rst_inv  = 1  
#        self.d14_read_oft = 480 // clk_period    
#        self.d14_read_wdt = 20  // clk_period    
#        self.d14_read_inv = 1 
#        self.d14_idxm_oft = 230 // clk_period    
#        self.d14_idxm_wdt = 270 // clk_period    
#        self.d14_idxm_inv = 0 
#        self.d14_idxl_oft = 480 // clk_period    
#        self.d14_idxl_wdt = 20  // clk_period    
#        self.d14_idxl_inv = 0 
#        self.d14_idl0_oft = 50  // clk_period    
#        self.d14_idl0_wdt = (190 // clk_period ) -1   
#        self.d14_idl1_oft = 480 // clk_period
#        self.d14_idl1_wdt = 20  // clk_period    
#        self.d14_idl_inv  = 0      
#
#        self.d58_rst_oft  = 0   // clk_period 
#        self.d58_rst_wdt  = (45  // clk_period ) 
#        self.d58_rst_inv  = 1  
#        self.d58_read_oft = 480 // clk_period 
#        self.d58_read_wdt = 20  // clk_period 
#        self.d58_read_inv = 1 
#        self.d58_idxm_oft = 230 // clk_period 
#        self.d58_idxm_wdt = 270 // clk_period 
#        self.d58_idxm_inv = 0 
#        self.d58_idxl_oft = 480 // clk_period 
#        self.d58_idxl_wdt = 20  // clk_period 
#        self.d58_idxl_inv = 0 
#        self.d58_idl0_oft = 50  // clk_period 
#        self.d58_idl0_wdt = (190 // clk_period ) -1
#        self.d58_idl1_oft = 480 // clk_period
#        self.d58_idl1_wdt = 20  // clk_period 
#        self.d58_idl_inv  = 0       
#####################external clokc phase for V323 firmware
#        self.d14_read_step = 11
#        self.d14_read_ud   = 0
#        self.d14_idxm_step = 9
#        self.d14_idxm_ud   = 0
#        self.d14_idxl_step = 7
#        self.d14_idxl_ud   = 0
#        self.d14_idl0_step = 12 
#        self.d14_idl0_ud   = 0
#        self.d14_idl1_step = 10 
#        self.d14_idl1_ud   = 0
#        self.d14_phase_en  = 1
#
#        self.d58_read_step = 0
#        self.d58_read_ud   = 0
#        self.d58_idxm_step = 5
#        self.d58_idxm_ud   = 0
#        self.d58_idxl_step = 4
#        self.d58_idxl_ud   = 1
#        self.d58_idl0_step = 3
#        self.d58_idl0_ud   = 0
#        self.d58_idl1_step = 4
#        self.d58_idl1_ud   = 0
#        self.d58_phase_en  = 1
#        self.fembs=[]
#        for wib_ip in self.WIB_IPs:
#            self.fembs.append({"WIB_IP":wib_ip, "FEMB":[1,1,1,1]})
    
