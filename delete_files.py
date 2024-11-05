# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Thu Oct 17 13:35:38 2024
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


rootpath = sys.argv[1]

for root, dirs, files in os.walk(rootpath):
    for fn in files:
        if ".png" in fn:
            try:
                os.remove(root + "/" + fn)
            except:
                print ("can't delete {}".format(fn))
                pass
