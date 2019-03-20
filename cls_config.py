# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 3/20/2019 6:09:39 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

import sys 
import string
import time
import struct
from cls_udp import CLS_UDP

class CLS_CONFIG:
    def __init__(self):
        self.UDP = CLS_UDP()
        self.WIB_IPs = ["192.168.121.1", "192.168.121.2", "192.168.121.3", \
                        "192.168.121.4", "192.168.121.5", "192.168.121.6",] #WIB IPs connected to host-PC
        self.MBB_IP  = "192.168.121.10"

    def WIB_SCAN(self, wib_verid=0x109):
        for wib_ip in self.WIB_IPs:
            self.UDP.UDP_IP = wib_ip
            self.UDP.jumbo_flag = self.jumbo_flag
            for i in range(5):
                wib_ver_rb = self.UDP.read_reg_wib (0xFF)
                if ((wib_ver_rb&0x0FFF) == wib_verid) and ( wib_ver_rb!= -1):
                    print ("WIB with IP = %s is found"%wib_ip) 
                    break
                time.sleep(0.1)
                if (i == 4):
                    print ("WIB with IP = %s isn't mounted, mask this IP"%wib_ip) 
                    self.WIB_IPs.remove(wib_ip)



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
#    
