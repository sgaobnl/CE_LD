# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 4/29/2025 2:00:35 PM
"""

import numpy as np
import struct
import os
from sys import exit
import sys
import os.path

def record_save(thr_ds, t, fp="./test_record.csv"):
    if os.path.isfile(fp):    
        with open(fp,"a+") as f:
            f.write("############################################\n")
            f.write("############################################\n")
            f.write("Time_of_Trig_set,%s,\n"%t)
            for ak in thr_ds.keys():
                if ak != "note":
                    f.write(ak + ","+ "%d"%thr_ds[ak] + ",\n")
                else:
                    f.write(ak + ","+ "%s"%thr_ds[ak] + ",\n")
            f.write("********************************************\n")
    else:
        pass
