# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Sat Mar  9 15:50:58 2024
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
import pickle
from shutil import copyfile
import operator


def FEREGS_CHK(feregs, asicno, asicch):
    if asicno%2 == 0:
        if asicch%4 == 0:
            asicchreg = (feregs[(asicno*18//4) + 3 - (asicch//4)] & 0xff000000)>>24
        elif asicch%4 == 1:
            asicchreg = (feregs[(asicno*18//4) + 3 - (asicch//4)] & 0x00ff0000)>>16
        elif asicch%4 == 2:
            asicchreg = (feregs[(asicno*18//4) + 3 - (asicch//4)] & 0x0000ff00)>>8
        elif asicch%4 == 3:
            asicchreg = (feregs[(asicno*18//4) + 3 - (asicch//4)] & 0x000000ff)
        asicglb1 = feregs[(asicno*18//4) + 4]&0xff 
        a = (feregs[(asicno*18//4) + 4]&0xff00)>>8
    elif asicno%2 == 1:
        if asicch==15:
            asicchreg = (feregs[(asicno*18//4) + 0]&0xff0000)>>16 
        if asicch==14:
            asicchreg = (feregs[(asicno*18//4) + 0]&0xff000000)>>24
        if asicch==13:
            asicchreg = (feregs[(asicno*18//4) + 1]&0xff)>>0 
        if asicch==12:
            asicchreg = (feregs[(asicno*18//4) + 1]&0xff00)>>8 
        if asicch==11:
            asicchreg = (feregs[(asicno*18//4) + 1]&0xff0000)>>16 
        if asicch==10:
            asicchreg = (feregs[(asicno*18//4) + 1]&0xff000000)>>24
        if asicch==9:
            asicchreg = (feregs[(asicno*18//4) + 2]&0xff)>>0 
        if asicch==8:
            asicchreg = (feregs[(asicno*18//4) + 2]&0xff00)>>8 
        if asicch==7:
            asicchreg = (feregs[(asicno*18//4) + 2]&0xff0000)>>16 
        if asicch==6:
            asicchreg = (feregs[(asicno*18//4) + 2]&0xff000000)>>24
        if asicch==5:
            asicchreg = (feregs[(asicno*18//4) + 3]&0xff)>>0 
        if asicch==4:
            asicchreg = (feregs[(asicno*18//4) + 3]&0xff00)>>8 
        if asicch==3:
            asicchreg = (feregs[(asicno*18//4) + 3]&0xff0000)>>16 
        if asicch==2:
            asicchreg = (feregs[(asicno*18//4) + 3]&0xff000000)>>24
        if asicch==1:
            asicchreg = (feregs[(asicno*18//4) + 4]&0xff)>>0 
        if asicch==0:
            asicchreg = (feregs[(asicno*18//4) + 4]&0xff00)>>8 
        asicglb1 = (feregs[(asicno*18//4) + 4]&0xff0000)>>16
        a = (feregs[(asicno*18//4) + 4]&0xff000000)>>24
    return asicchreg, asicglb1, a

#fn = """/Users/shanshangao/Downloads/SBND_LD/LD/2024_02_16/LD_2024_02_16_12_42_33/WIB_10_226_34_46FEMB_1_Time2024_02_16_12_42_56.femb"""
##fn = """/Users/shanshangao/Downloads/SBND_LD/LD/2024_02_16/LD_2024_02_16_12_42_33/WIB_10_226_34_45FEMB_1_Time2024_02_16_12_42_55.wib"""
#with open (fn, "rb") as fs:
#    raw2 = pickle.load(fs)
#
#for i in range(len(regs)):
#    print ("Reg %x, Value %x, %x"%(regs[i][0], regs[i][1], raw2[i][1]))


#fn = """/Users/shanshangao/Downloads/SBND_LD/LD/2024_02_16/LD_2024_02_16_12_42_33/WIB_10_226_34_46FEMB_0_Time2024_02_16_12_42_56.femb"""
#fn = """/Users/shanshangao/Downloads/SBND_LD/LD_2024_02_16_12_42_33/WIB_10_226_34_45FEMB_0_Time2024_02_16_12_42_55.wib"""

def FEMBREG_Process(fn):
    if (".femb" in fn[-5:]) and ("WIB_10_226_34_" in fn) and ("FEMB_" in fn):
        crateno = int(fn[fn.find("WIB_10_226_34_")+14])
        wibno = int(fn[fn.find("WIB_10_226_34_")+15])-1
        fembno = int(fn[fn.find("FEMB_")+5])
        with open (fn, "rb") as fs:
            regs = pickle.load(fs)
    
            fewrregs = []
            ferdregs = []
            for i in range(len(regs)):
                if (regs[i][0] == 0x05) :#address
                    fpgadac_v = regs[i][1] & 0x3F
                    pls_dly = (regs[i][1] & 0xFF00)>>8 #10ns/step
                    pls_period = (regs[i][1] & 0xFFFF0000)>>16 #test pulse period 2MS/s
                if (regs[i][0] == 0x08) :#address
                    data_stream_enable = (regs[i][1] & 0x10)>>4
                    sys_clk_flg = (regs[i][1] & 0x10000)>>16
                if (regs[i][0] == 0x09) :#address
                    stream_en = (regs[i][1] & 0x01)
                    prbs_en = (regs[i][1] & 0x02)>>1
                    cnt_en = (regs[i][1] & 0x04)>>2
                    adc_data_en = (regs[i][1] & 0x08)>>3
                if (regs[i][0] == 0x10) :#address
                    fpga_tp_en = (regs[i][1] & 0x01)
                    asic_tp_en = (regs[i][1] & 0x02)>>1
                    dac_sel = (regs[i][1] & 0x04)>>2 #0 internal, 1 external
                if (regs[i][0] == 0x12) :#address
                    int_tp_en = (regs[i][1] & 0x01) #0 enable, 1 disable
                    ext_tp_en = (regs[i][1] & 0x02)>>1 #0 enable, 1 disable
                if (regs[i][0] == 0x13) :#address
                    femb_tst_mode = (regs[i][1] & 0x01) 
                if (regs[i][0] == 0x2A) :#address
                    femb_tst_sel = (regs[i][1] & 0x0f) #
                    femb_no = (regs[i][1] & 0xf0)>>4 #
                if (regs[i][0] == 0x2B) :#address
                    pls_width = (regs[i][1] & 0xffff) #
                if (regs[i][0] >= 0x200) and (regs[i][0] <= 0x223) :
                    fewrregs.append(regs[i][1])
                if (regs[i][0] >= 0x250) and (regs[i][0] <= 0x273) :
                    ferdregs.append(regs[i][1])
    
            fechns = []
            for ch in range(128):
                fechns.append([])
                fechns[ch] = [crateno, wibno, fembno, ch, fpgadac_v, pls_dly, pls_period,  sys_clk_flg, fpga_tp_en, asic_tp_en, dac_sel, int_tp_en, ext_tp_en, femb_tst_sel, femb_tst_sel, pls_width] 
                asicno = ch//16
                asicch = ch%16
                asicwrchreg, asicwrglb1, asicwrglb2 = FEREGS_CHK(fewrregs, asicno, asicch)
                asicrdchreg, asicrdglb1, asicrdglb2 = FEREGS_CHK(ferdregs, asicno, asicch)
                if asicwrchreg != asicrdchreg:
                    fechns[ch].append(True)
                else:
                    fechns[ch].append(False)
                if asicwrglb1 != asicrdglb1:
                    fechns[ch].append(True)
                else:
                    fechns[ch].append(False)
                if asicwrglb2 != asicrdglb2:
                    fechns[ch].append(True)
                else:
                    fechns[ch].append(False)
                sdac = (asicrdglb2>>7)&0x01 + ((asicrdglb2>>6)&0x01)*2 + ((asicrdglb2>>5)&0x01)*4  + ((asicrdglb2>>4)&0x01)*8  + ((asicrdglb2>>3)&0x01)*16  + ((asicrdglb2>>2)&0x01)*32 
                sdacsw1 =  (asicrdglb2>>1)&0x01 
                sdacsw2 =  (asicrdglb2>>0)&0x01 
            #    if sdacsw1 == 1:
            #        cali_src_s = "1_External"
            #    else:
            #        cali_src_s= "0_Internal"
            #    if sdacsw1 == 1:
            #        asic_dac_s = "1_ASIC_DAC_Enable"
            #    else:
            #        asic_dac_s = "0_ASIC_DAC_Disbale"
                slk =   asicrdglb1&0x01
                stb1 = (asicrdglb1&0x02)>>1
                stb  = (asicrdglb1&0x04)>>2
                s16  = (asicrdglb1&0x08)>>3
                slkh = (asicrdglb1&0x10)>>4
                sdc  = (asicrdglb1&0x20)>>5
                res0 = (asicrdglb1&0x40)>>6
                res1 = (asicrdglb1&0x80)>>7
            #    if (slk == 0) and (slkh == 0):
            #        slk_s = "500pA"
            #    elif (slk == 1) and (slkh == 0):
            #        slk_s = "100pA"
            #    elif (slk == 1) and (slkh == 1):
            #        slk_s = "1nA"
            #    elif (slk == 0) and (slkh == 1):
            #        slk_s = "5nA"
            #    if sdc == 1:
            #        sdc_s = "AC"
            #    else:
            #        sdc_s = "DC"
                sdf = (asicrdchreg&0x01)>>0
                smn = (asicrdchreg&0x02)>>1
                st1 = (asicrdchreg&0x04)>>2
                st0 = (asicrdchreg&0x08)>>3
                sg1 = (asicrdchreg&0x10)>>4
                sg0 = (asicrdchreg&0x20)>>5
                snc = (asicrdchreg&0x40)>>6
                sts = (asicrdchreg&0x80)>>7
                fechns[ch].append([sts,snc,sg0,sg1,st0,st1,smn,sdf,sdc,slkh,s16,stb,stb1,slk,sdacsw1,sdacsw2,sdac])
            return fechns
    else:
        return None

fechns = FEMBREG_Process(fn)

print (fechns[0])
    
#
#
#for i in range(len(fewrregs)):
#    if fewrregs[i] != ferdregs[i] :
#        print ("Error")
#    else:
#        print (hex(fewrregs[i]), hex(fewrregs[i]))
#
##for adr in range(0x200, 0x223, 1):
##    if regs[adr]


