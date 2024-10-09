'''
This program was written by Varuna Meddage
on 10/11/2023
to check the AM_28 current of all FEMBs connected to a WIB
during noise tests.
This current value is an indication of
whether the protection diodes on FEMBs are 
turned on or turned off.

Update by Sungbin Oh to report values to EPICS by running this script from wibfemb_monitor.py
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
import epics
from epics import caget, caput, cainfo
import argparse

# Modify to accept arguments from the command line
def main():
        parser = argparse.ArgumentParser(description="Enter crate number and PTB slot number.")
        parser.add_argument("crateno", type=int, help="Crate number (1-4)")
        parser.add_argument("PTBslotno", type=int, help="PTB slot number (1-6)")
    
        args = parser.parse_args()

        crateno = args.crateno
        PTBslotno = args.PTBslotno

        if (crateno > 4 or crateno < 1):
                print("Crate number entered ", crateno, " is an invalid number. Exiting the program.")
                sys.exit()
        elif (PTBslotno > 6 or PTBslotno < 1):
                print("PTB slot number entered ", PTBslotno, " is an invalid number. Exiting the program.")
                sys.exit()

        wib_ip = "10.226.34." + str(crateno * 10 + PTBslotno)
        cls = CLS_CONFIG() 
        cls.WIB_ver = 0x125
        stats = cls.WIB_STATUS(wib_ip)
        keys = list(stats.keys())

        timestamp = time.time()
        date_time = datetime.fromtimestamp(timestamp)
        print("================== Setting EPICS PVs for crate" + str(crateno) + ", slot" + str(PTBslotno) + ", " + str(date_time) + " =====================")
        
        epics_pv_prefix = "sbnd_ce_crate" + str(crateno) + "_wib" + str(PTBslotno) + "/"

        for key in keys:
                if key == "TIME":
                        #print(key, stats[key])
                        this_pv_name = epics_pv_prefix + "PythonTimestamp"
                        this_timestamp = time.time()
                        #print(this_timestamp)
                        caput(this_pv_name, this_timestamp)
                        this_pv_value = caget(this_pv_name)
                        #print(this_pv_name, this_pv_value)
                else:
                        #print(key, stats[key])
                        this_pv_name = epics_pv_prefix + key
                        caput(this_pv_name, stats[key])
                        this_pv_value = caget(this_pv_name)
                        #print(this_pv_name, this_pv_value)

if __name__ == "__main__":
    main()
