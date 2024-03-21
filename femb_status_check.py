'''
This program was written by Varuna Meddage
on 10/11/2023
to check the AM_28 current of all FEMBs connected to a WIB
during noise tests.
This current value is an indication of
whether the protection diodes on FEMBs are 
turned on or turned off.
'''

import numpy as np
import sys 
import os
import string
import time
from datetime import datetime
import struct
import codecs
from cls_config import CLS_CONFIG
from raw_convertor import RAW_CONV
import pickle
from shutil import copyfile
from femb_qc import FEMB_QC

crateno = int(input("Crate no(1-4): "))
PTBslotno = int(input("PTB slot no(1-6): "))
if (crateno>4 or crateno<1):
	print("Crate number entered ", crateno, " is an invalid number. Exiting the program.")
	sys.exit()
elif (PTBslotno>6 or PTBslotno<1):
	print("PTB slot number entered ", PTBslotno, " is an invalid number. Exiting the program.")
	sys.exit()
wib_ip = "10.226.34."+str(crateno*10 + PTBslotno)
cls = CLS_CONFIG() 
cls.WIB_ver = 0x125
stats = cls.WIB_STATUS(wib_ip)
keys = list(stats.keys())

print ("================== CHECKING FEMB STATUS =====================")

for key in keys:
    print (key, stats[key])

for i in range(4):
   for key in keys:
      if key in "FEMB%d_AMV28_I"%i:
         print ("AM V28 current in FEMB ",i+1, " is : ", stats[key])

for i in range(4):
   for key in keys:
      if key in "FEMB%d_AMV28_V"%i:
         print ("AM V28 voltage in FEMB ",i+1, " is : ", stats[key])
   
for i in range(4):
   for key in keys:
      if key in "FEMB%d_AMV33_V"%i:
         print ("AM V33 voltage in FEMB ",i+1, " is : ", stats[key])



