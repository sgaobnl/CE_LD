# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Tue May  7 13:42:07 2019
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

###########Change to your local path##########
userdir = "/Users/shanshangao/tmp/SBND_CHKOUT/"
##############################################

from femb_qc import FEMB_QC
a = FEMB_QC()
a.userdir = userdir 
a.env = "RT"
a.avg_cnt = 100
a.CLS.val = 2000
a.re_init()
FEMB_infos = a.FEMB_CHKOUT_Input()
a.FEMB_CHKOUT(FEMB_infos, pwr_int_f = False, testcode = 3 )
print ("Well Done")


