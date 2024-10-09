'''
This program was written by Varuna Meddage
on 10/11/2023
to check the AM_28 current of all FEMBs connected to a WIB
during noise tests.
This current value is an indication of
whether the protection diodes on FEMBs are 
turned on or turned off.

Update by Sungbin Oh to reset EPICS PVs when wibfemb_monitor.py is stopped using ctrl+C
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
        print("================== Resetting EPICS PVs to -1 for crate" + str(crateno) + ", slot" + str(PTBslotno) + ", " + str(date_time) + " =====================")

        epics_pv_prefix = "sbnd_ce_crate" + str(crateno) + "_wib" + str(PTBslotno) + "/"

        for key in keys:
                if key == "TIME":
                        this_pv_name = epics_pv_prefix + "PythonTimestamp"
                        this_timestamp = time.time()
                        caput(this_pv_name, this_timestamp)
                        this_pv_value = caget(this_pv_name)
                else:
                        this_pv_name = epics_pv_prefix + key
                        caput(this_pv_name, -1)
                        this_pv_value = caget(this_pv_name)

if __name__ == "__main__":
    main()
