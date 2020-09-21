# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description:
Created Time: 7/15/2016 11:47:39 AM
Last modified: Sat Nov 24 11:43:33 2018
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
#from openpyxl import Workbook
import numpy as np
import struct
import os
from sys import exit
import os.path
import math
import copy
import sys


import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab
import statsmodels.api as sm

fig = plt.figure(figsize=(16,10))

bnlc = [  0,  22 , 27 , 33 , 47 , 50 ,100 ,150]
bnle =[207.0, 246.0, 241.5, 269.5, 298.5, 300.0, 411.0, 515.0]
bnlstd =[8.8801544388114593, 4.0, 7.5, 5.5, 4.5, 5.0, 5.3385391260156556, 9.8994949366116654]
bnlw = np.array(bnlc)/18.1
bnlr = sm.OLS(bnle,sm.add_constant(bnlw)).fit()
bnlr_a= bnlr.params[1]
bnlr_b= bnlr.params[0]
plt.errorbar(bnlw, bnle, bnlstd, fmt='o', color ='C0')
plt.plot(bnlw, bnlw*bnlr_a+bnlr_b, label= "Mica Caps(LN2) Raw Data", color='C0')

mbx = [2.5, 4.8, 4.8]
mbe = [350, 490, 480]
fmbe = [300, 380, 400]
plt.scatter(mbx, mbe, marker='p', color ='C1', label = "MicroBooNE(LAr) Raw Data")
plt.scatter(mbx, fmbe, marker='*', color ='C2', label = "MicroBooNE(LAr) Filtered Data")

apa40x = [2.8, 4, 4]
apa40e = [332, 383, 395]
apa40s = [21, 24, 19]
plt.errorbar(apa40x, apa40e, apa40s, color = "C3", fmt='h', label = "40% APA(LN2) Raw Data")
fapa40e = [318, 325, 352]
plt.scatter(apa40x, fapa40e, marker='+', color ='C4', label = "40% APA(LN2) Filtered Data")

pdx = [6, 7.39, 7.39]
pde = [565, 662, 651]
pds = [60, 56, 54]
plt.errorbar(pdx, pde, pds, color = "C5", fmt='x', label = "ProtoDUNE(LAr) Raw Data")
pdef = [468, 540, 540]
pdsf = [71, 80, 80]
plt.errorbar(pdx, pdef, pdsf, color = "C6", fmt='D', label = "ProtoDUNE(LAr) Filtered Data")

rawx = np.array( mbx  + pdx)
rawx = np.insert(rawx, 0, 0)
rawy = mbe  + pde
rawy = np.insert(rawy, 0, 207)
rraw = sm.OLS(rawy, sm.add_constant(rawx)).fit()
rraw_a= rraw.params[1]
rraw_b = rraw.params[0]
rawxx = np.insert(rawx,0, 0)
rawxx = np.append(rawxx,8.2)
plt.plot(rawxx, rawxx*rraw_a+rraw_b,  color='r', label = "Fitting with MicroBooNE and ProtoDUNE Raw Data")

idx = [0.95, 1.18, 1.18]
ide = [331, 325, 325]
ids = [60, 55, 55]
plt.errorbar(idx, ide, ids, color = "C8", fmt='>', label = "ICEBERG(LAr) Raw Data")
idef = [313, 295, 295]
idsf = [56, 45, 45]
plt.errorbar(idx, idef, idsf, color = "C9", fmt='<', label = "ICEBERG(LAr) Filtered Data")

fy = fmbe  + pdef
fy = np.insert(fy, 0, 207)
fr = sm.OLS(fy, sm.add_constant(rawx)).fit()
fr_a= fr.params[1]
fr_b = fr.params[0]
frxx = np.insert(rawx,0, 0)
frxx = np.append(frxx,8.2)
plt.plot(frxx, frxx*fr_a+fr_b,  color='g', label = "Fitting with MicroBooNE and ProtoDUNE Filtered Data")


plt.title("Noise Performance", fontsize = 24 )
plt.ylabel("ENC / e$^-$", fontsize = 20 )
plt.xlabel("Equivalent Wire Length (18.1pF/m) / m ", fontsize = 20 )
plt.xlim([-1,10])
plt.ylim([0,1000])
plt.tick_params(labelsize=20)
#plt.grid(axis="y")
plt.grid()
plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
plt.legend(loc='best', fontsize=16)
#plt.show()
plt.savefig("./ENP_projection.png")
plt.close()

