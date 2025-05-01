# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/30/2025 2:12:26 PM
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
from cls_udp_trig import CLS_UDP
from fe_reg_mapping import FE_REG_MAPPING
import pickle
from setdatadir import savedir 
import multiprocessing
from csv_read import thr_read
from record_save import record_save

class CLS_CONFIG:
    def __init__(self):
        self.jumbo_flag = True 
        self.FEMB_ver = 0x501
        self.UDP = CLS_UDP()
        self.UDP.jumbo_flag = self.jumbo_flag
        self.UDP.UDP_IP = "192.168.121.1"
        self.FEREG_MAP = FE_REG_MAPPING()

    def CE_VER_CHK(self ):
        a = self.UDP.read_reg( 0x101)
        print ("version:", hex(a))
        if a&(0x501) != 0x501:
            exit()
        self.CE_RST( )
        self.UDP.write_reg_checked ( 10, 0xEFB)
        print ("Jambo frame enabled")
        time.sleep(1)

    def CE_RST(self ):
        self.UDP.write_reg( 0, 1)

    def CE_CHK_CFG(self, \
                   pls_cs=0, dac_sel=0, fpgadac_en=0, asicdac_en=0, fpgadac_v=0, \
                   pls_gap = 500, pls_dly = 10, mon_cs=0, \
                   data_cs = 0, \
                   sts=0, snc=0, sg0=0, sg1=1, st0=1, st1=1, smn=0, sdf=1, \
                   slk0 = 0, stb1 = 0, stb = 0, s16=0, slk1=0, sdc=0, sdd=0, sgp=0, swdac=0, dac=0, \
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

        time.sleep(0.001)
        if self.jumbo_flag :
            self.UDP.write_reg_checked ( 44, 0xEFB)
        else:
            self.UDP.write_reg_checked ( 44, 0x1FB)

        self.UDP.write_reg_checked ( 5, reg_5_value)
        self.UDP.write_reg_checked (8, data_cs&0x0F)
        #self.UDP.write_reg_checked (9, test_pulse_width), to be added later

        self.UDP.write_reg_checked (16, tp_sel&0x0000ffff)
        self.UDP.write_reg_checked (18, pls_cs_value)
        #self.UDP.write_reg_checked (19, 0) #FEMB_TST_MODE, to be added later

        #FE configuration
        self.FEREG_MAP.set_fe_board(sts, snc, sg0, sg1, st0, st1, smn, sdf,\
                                    slk0, stb1, stb, s16, slk1, sdc, sdd, sgp, swdac, dac)
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
        time.sleep(5)

        self.UDP.write_reg_checked( 7, 0) 


    def Trig_threshold(self, thr_ds ):
        trig_en = thr_ds["trig_en"]
        ext_trig_en = thr_ds["ext_trig_en"]
        glb_thr_en = thr_ds["glb_thr_en"]
        glb_thr_val = thr_ds["glb_thr_val"]
        pre_samN = thr_ds["pre_samN"]
        total_samN = thr_ds["total_samN"]
        trig_mask = thr_ds["trig_mask"]
        chip0 = [thr_ds["ch00"], 
                 thr_ds["ch01"], 
                 thr_ds["ch02"], 
                 thr_ds["ch03"], 
                 thr_ds["ch04"], 
                 thr_ds["ch05"], 
                 thr_ds["ch06"], 
                 thr_ds["ch07"], 
                 thr_ds["ch08"], 
                 thr_ds["ch09"], 
                 thr_ds["ch10"], 
                 thr_ds["ch11"], 
                 thr_ds["ch12"], 
                 thr_ds["ch13"], 
                 thr_ds["ch14"], 
                 thr_ds["ch15"] 
                 ]
        chip1 = [thr_ds["ch16"], 
                 thr_ds["ch17"], 
                 thr_ds["ch18"], 
                 thr_ds["ch19"], 
                 thr_ds["ch20"], 
                 thr_ds["ch21"], 
                 thr_ds["ch22"], 
                 thr_ds["ch23"], 
                 thr_ds["ch24"], 
                 thr_ds["ch25"], 
                 thr_ds["ch26"], 
                 thr_ds["ch27"], 
                 thr_ds["ch28"], 
                 thr_ds["ch29"], 
                 thr_ds["ch30"], 
                 thr_ds["ch31"] 
                 ]

        self.UDP.write_reg_checked( 7, 0) #disable data
        time.sleep(0.1)

        if ext_trig_en == 1:
            self.UDP.write_reg_checked ( 20, 1)  #enable external trigger
        else:
            self.UDP.write_reg_checked ( 20, 0)  #enable external trigger

        #self.UDP.write_reg_checked ( 15, trig_edge&0x01)  #0--falling edge, 1 rising edge 

        samN = ((total_samN&0xff)<<16) + (pre_samN&0xff)
        self.UDP.write_reg_checked ( 14, samN) 
        self.UDP.write_reg_checked ( 12, trig_mask) 
        if glb_thr_en == 1:
            self.UDP.write_reg_checked ( 11, 0x80000000|(((glb_thr_val&0x0fff)<<16)  + (glb_thr_val&0xfff))) 

        self.UDP.write_reg_checked ( 25, ((chip1[0]&0x0fff)<<16)  + (chip0[0]&0xfff)) #ch16, 0
        self.UDP.write_reg_checked ( 26, ((chip1[1]&0x0fff)<<16)  + (chip0[1]&0xfff)) 
        self.UDP.write_reg_checked ( 27, ((chip1[2]&0x0fff)<<16)  + (chip0[2]&0xfff)) 
        self.UDP.write_reg_checked ( 28, ((chip1[3]&0x0fff)<<16)  + (chip0[3]&0xfff)) 
        self.UDP.write_reg_checked ( 29, ((chip1[4]&0x0fff)<<16)  + (chip0[4]&0xfff)) 
        self.UDP.write_reg_checked ( 30, ((chip1[5]&0x0fff)<<16)  + (chip0[5]&0xfff)) 
        self.UDP.write_reg_checked ( 31, ((chip1[6]&0x0fff)<<16)  + (chip0[6]&0xfff)) 
        self.UDP.write_reg_checked ( 32, ((chip1[7]&0x0fff)<<16)  + (chip0[7]&0xfff)) 
        self.UDP.write_reg_checked ( 33, ((chip1[8]&0x0fff)<<16)  + (chip0[8]&0xfff)) 
        self.UDP.write_reg_checked ( 34, ((chip1[9]&0x0fff)<<16)  + (chip0[9]&0xfff)) 
        self.UDP.write_reg_checked ( 35, ((chip1[10]&0x0fff)<<16) + (chip0[10]&0xfff)) 
        self.UDP.write_reg_checked ( 36, ((chip1[11]&0x0fff)<<16) + (chip0[11]&0xfff)) 
        self.UDP.write_reg_checked ( 37, ((chip1[12]&0x0fff)<<16) + (chip0[12]&0xfff)) 
        self.UDP.write_reg_checked ( 38, ((chip1[13]&0x0fff)<<16) + (chip0[13]&0xfff)) 
        self.UDP.write_reg_checked ( 39, ((chip1[14]&0x0fff)<<16) + (chip0[14]&0xfff)) 
        self.UDP.write_reg_checked ( 40, ((chip1[15]&0x0fff)<<16) + (chip0[15]&0xfff)) 

        if trig_en == 1:
            self.UDP.write_reg_checked( 7, 1) #enable data
            time.sleep(1)
            self.UDP.write_reg_checked ( 13, 1) #enable trigger mode
            time.sleep(0.5)
            self.Trig_rst()
        else:
            self.UDP.write_reg_checked ( 13, 0) #disable trigger mode

    def Trig_rst(self):
        self.UDP.write_reg_checked ( 10, 1) 
        time.sleep(0.1)
        self.UDP.write_reg_checked ( 10, 0)

                       
    def CE_ACQ(self, val=100):
        self.UDP.write_reg_checked( 7, 1) #enable data
        time.sleep(0.1)
        data = []
        for chip in range(2):
            self.UDP.write_reg_checked ( 0x06, chip)
            rawdata = cls.UDP.get_rawdata_packets(val)  
            data.append(rawdata)
        self.UDP.write_reg_checked( 7, 0) 
        return data

    def CE_ACQ_trig(self, val=100):
        rawdata = self.UDP.get_rawdata_packets(val)  
#        self.UDP.write_reg_checked( 7, 0) 
        return rawdata

    def get_rawdata_trig(self, fdir="./", thr_ds=None):
        # Create a Queue for communication between processes
        data_queue = multiprocessing.Queue()

        # Create two processes: one for receiving data, another for saving data
        receive_process = multiprocessing.Process(target=self.UDP.get_rawdata_trig_rece, args=(data_queue,))
        save_process = multiprocessing.Process(target=self.UDP.get_rawdata_trig_save, args=(data_queue,fdir))

        # Start the processes
        receive_process.start()
        save_process.start()

        # Let the processes run for some time (e.g., 5 seconds for this demo)
        try:
            print ("start......")
            t0 = time.time()
            dlyt = 10
            xi = 0
            while True:
                t1 = time.time()
                t = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
                thr_ds_new = thr_read()
                if xi == dlyt:
                    print (t + ": data taking ongoing for %d seconds... (Ctrl + C to terminate the script)"%(int(t1-t0)))
                    xi = 0
                else:
                    xi = xi + 1
                if (thr_ds_new != thr_ds) and (thr_ds_new !=None):
                    thr_ds = thr_ds_new
                    cls.Trig_threshold(thr_ds)
                    record_save(thr_ds=thr_ds, t=t, fp="./test_record.csv" )
                    print ("New Trigger scheme is applied")
                    dlyt =thr_ds["flash"]+5
                time.sleep(1)
        except KeyboardInterrupt:
            print ("End the process! ")

        # Terminate the processes
        receive_process.terminate()
        save_process.terminate()

        # Join the processes to ensure proper cleanup
        receive_process.join()
        save_process.join()

#        print("Data receiving and saving completed.")


if __name__ == '__main__':
    cls = CLS_CONFIG()
    femb_id = int(sys.argv[1])
    if femb_id == 1:
        cls.UDP.UDP_IP = "192.168.121.1"
    elif femb_id ==2:
        cls.UDP.UDP_IP = "192.168.121.2"
    else:
        print ("Wrong uFEMB ID, exit")
        exit()

    cls.CE_VER_CHK()

#    #14mV/fC
#    sg0 = 0
#    sg1 = 0

    #4.7mV/fC
    sg0 = 1
    sg1 = 1


    #1.0us
#    st0 = 0
#    st1 = 0

    #1us
    st0 = 0
    st1 = 0

    cls.CE_CHK_CFG(pls_cs=0, asicdac_en=0, sts=0, snc=0, slk1=0, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sdf=1, dac=0, sgp=0, swdac=0, data_cs=0)
    #cls.CE_CHK_CFG(pls_cs=1, asicdac_en=1, sts=1, snc=1, sg0=sg0, sg1=sg1, st0=st0, st1=st1, sdf=1, dac=32, sgp=0, swdac=1, data_cs=0, pls_gap = 2000)

    if femb_id == 1:
        cls.UDP.write_reg_checked ( 17, 1) #reset sync_cnt
        time.sleep(1)
        cls.UDP.write_reg_checked ( 17, 0) #reset sync_cnt

    t1 = time.time()
    t = datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    thr_ds = thr_read()
    cls.Trig_threshold(thr_ds)
    record_save(thr_ds=thr_ds, t=t, fp="./test_record.csv" )

    ts = datetime.now().strftime("%Y%m%d_%H_%M")
    savedir = "D:/uFEMB/SiPM/Rawdata_%s/"%ts
    if (os.path.exists(savedir)):
        pass
    else:
        try:
            os.makedirs(savedir)
        except OSError:
            print ("Error to create folder %s"%savedir)
            sys.exit()

    cls.get_rawdata_trig(fdir = savedir, thr_ds=thr_ds)

    cls.UDP.write_reg_checked( 7, 0) #disable data
    print ("Well Done!")

