# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 3/18/2025 5:10:54 PM
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
from cls_udp import CLS_UDP
from fe_reg_mapping import FE_REG_MAPPING
import pickle

class CLS_CONFIG:
    def __init__(self):
        self.jumbo_flag = True 
        self.FEMB_ver = 0x501
        self.ip = "192.168.121.1"
        self.UDP = CLS_UDP()
        self.UDP.jumbo_flag = self.jumbo_flag
        self.UDP.UDP_IP = self.ip
        self.FEREG_MAP = FE_REG_MAPPING()

    def CE_VER_CHK(self ):
        print ("bbb")
        a = self.UDP.read_reg( 0x101)
        print (hex(a))
        print ("ccc")

    def CE_CHK_CFG(self, \
                   pls_cs=0, dac_sel=0, fpgadac_en=0, asicdac_en=0, fpgadac_v=0, \
                   pls_gap = 500, pls_dly = 10, mon_cs=0, \
                   data_cs = 0, \
                   sts=0, snc=0, sg0=0, sg1=1, st0=1, st1=1, smn=0, sdf=1, \
                   slk0 = 0, stb1 = 0, stb = 0, s16=0, slk1=0, sdc=0, swdac1=0, swdac2=0, dac=0, \
                  ):
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

        self.UDP.write_reg( 0, 1)
        time.sleep(0.001)
        if self.jumbo_flag :
            self.UDP.write_reg_checked ( 10, 0xEFB)
        else:
            self.UDP.write_reg_checked ( 10, 0x1FB)

        self.UDP.write_reg_checked ( 5, reg_5_value)
        self.UDP.write_reg_checked (16, tp_sel&0x0000ffff)
        self.UDP.write_reg_checked (18, pls_cs_value)
        self.UDP.write_reg_checked (42, data_cs&0x0F)
#        self.UDP.write_reg_checked (42, 1)

        #FE configuration
        self.FEREG_MAP.set_fe_board(sts, snc, sg0, sg1, st0, st1, smn, sdf,\
                                    slk0, stb1, stb, s16, slk1, sdc, swdac1, swdac2, dac)
        regs = self.FEREG_MAP.REGS
        fe_regs = [0x00000000]*(8+1)*4
        #@for chip in [0,2,4,6]:
        for chip in [0]:
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
        #for regNum in range(0x200,0x200+len(fe_regs),1):
        for regNum in range(0x200,0x200+9,1):
            self.UDP.write_reg_checked ( regNum, fe_regs[i])
            i = i + 1
        self.UDP.write_reg ( 2, 1) #SPI write
        time.sleep(0.001)
        self.UDP.write_reg ( 2, 1) #SPI write
        time.sleep(0.001)
        self.UDP.write_reg ( 2, 1) #SPI write
        time.sleep(0.001)
        fe_rb_regs = []
        #for regNum in range(0x250,0x250+len(fe_regs),1):
        for regNum in range(0x250,0x250+9,1):
            val = self.UDP.read_reg ( regNum ) 
            fe_rb_regs.append( val )
        j = 0
        for j in range(9):
            if (fe_regs[j] != fe_rb_regs[j]) and (data_cs == 0 ):
                print ("%dth, %8x,%8x"%(j, fe_regs[j],fe_rb_regs[j]))
                print ("FE-ADC 0 SPI failed, exit anyway")
                exit()

        self.UDP.write_reg_checked( 7, 0) 
        time.sleep(1)
        self.UDP.write_reg_checked( 7, 1) #enable data

if __name__ == '__main__':
   cls = CLS_CONFIG()
   cls.CE_VER_CHK()
   cls.CE_CHK_CFG(data_cs=0)
   rawdata = cls.UDP.get_rawdata_packets(100)  
   print ("done")
