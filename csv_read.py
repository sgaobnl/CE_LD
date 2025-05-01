# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/29/2025 1:58:59 PM
"""

import numpy as np
import struct
import os
from sys import exit
import sys
import os.path

def thr_read(fp="./thresholds_new.csv"):
    thr_ds = {"trig_en":1, 
              "ext_trig_en":1,
              "glb_thr_en":0,
              "glb_thr_val":1000,
              "pre_samN":40,
              "total_samN":140,
              "trig_mask":0x00000000,
              "ch00":1800,
              "ch01":1800,
              "ch02":1800,
              "ch03":1800,
              "ch04":1800,
              "ch05":1800,
              "ch06":1800,
              "ch07":1800,
              "ch08":1800,
              "ch09":1800,
              "ch10":1800,
              "ch10":1800,
              "ch11":1800,
              "ch12":1800,
              "ch13":1800,
              "ch14":1800,
              "ch15":1800,
              "ch16":1800,
              "ch17":1800,
              "ch18":1800,
              "ch19":1800,
              "ch20":1800,
              "ch21":1800,
              "ch22":1800,
              "ch23":1800,
              "ch24":1800,
              "ch25":1800,
              "ch26":1800,
              "ch27":1800,
              "ch28":1800,
              "ch29":1800,
              "ch30":1800,
              "ch31":1800,
              "flash":60,
              "note": "debug",
              }
    if os.path.isfile(fp):    
        with open(fp,"r") as f:
            for line in f:
                tmps = line.split(",")
                try:
                    if tmps[0] == "trig_en":
                        nval = int(tmps[1])
                        thr_ds[tmps[0]] = nval&0x01
                    elif tmps[0] == "ext_trig_en":
                        nval = int(tmps[1])
                        thr_ds[tmps[0]] = nval&0x01
                    elif tmps[0] == "glb_thr_en":
                        nval = int(tmps[1])
                        thr_ds[tmps[0]] = nval&0x01
                    elif tmps[0] == "glb_thr_val":
                        nval = int(tmps[1])
                        thr_ds[tmps[0]] = nval&0xFFF
                    elif tmps[0] == "pre_samN":
                        nval = int(tmps[1])
                        thr_ds[tmps[0]] = nval&0x7F
                    elif tmps[0] == "total_samN":
                        nval = int(tmps[1])
                        thr_ds[tmps[0]] = nval&0xFF
                    elif tmps[0] == "trig_mask":
                        nval = int(tmps[1],16)
                        thr_ds[tmps[0]] = nval&0xFFFFFFFF
                    elif tmps[0][0:2] == "ch":
                        nval = int(tmps[1])
                        thr_ds[tmps[0]] = nval&0xFFF
                    elif tmps[0] == "flash":
                        nval = int(tmps[1])
                        thr_ds[tmps[0]] = nval&0xFFFF
                    elif tmps[0] == "note":
                        thr_ds[tmps[0]] = tmps[1]
                except ValueError:
                    print (tmps)
                    return  None
        return thr_ds
    else:
        return None

#fp = "./thresholds_new.csv"
#thr_ds =  thr_read(fp)
#print (thr_ds)
