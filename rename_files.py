# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: 5/13/2025 10:30:52 AM
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
import pickle
import shutil
import numpy as np
rds = [ "Bakata_20250505_15_57/", "Bakata_20250505_17_45", "Bakata_20250509_12_35", "Bakata_20250509_12_38"]

rootdir = """G:/SiPM/"""

for srcd in rds:
    srcdir = rootdir + srcd + "/"
    print (srcdir)
    files = []
    for root, dirs, files in os.walk(srcdir):
        files = files
        break
    if len(files) > 0:
        pass
    else:
        continue

    for fn in files:
        crt = os.path.getmtime(srcdir + fn)
        fct =datetime.fromtimestamp(crt).strftime("%Y%m%d_%H_%M_")
        fup = fn.find("uFEMB")
        if fup != 0:
            print (fn)
            nfn = fn[fup:]
            #print (nfn)
            print (nfn)
            os.rename(srcdir+fn, srcdir+nfn)
            if "_2025" not in nfn:
                nfn2=nfn[0:7] + fct + nfn[7:]
                os.rename(srcdir+nfn, srcdir+nfn2)


        if fup == 0:
            nfn = fn[fup:]
            if "_2025" not in nfn:
                nfn=nfn[0:7] + fct + nfn[7:]
            #    print (nfn)
                os.rename(srcdir+fn, srcdir+nfn)



