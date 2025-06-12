import time
import sys
import numpy as np
import pyvisa  
from datetime import datetime


def sg_control(period=300):
    try:
        rm = pyvisa.ResourceManager()
        sig_gen = rm.open_resource('TCPIP0::192.168.123.3::inst0::INSTR')
        print(sig_gen.query("*IDN?"),end='')
        sig_gen.write('Output{} {}'.format(1, "ON"))
        sig_gen.write('Output{} {}'.format(2, "ON"))
        time.sleep(60)
        sig_gen.write('Output{} {}'.format(2, "OFF"))
        sig_gen.write('Output{} {}'.format(1, "OFF"))
        sig_gen.close() 
    except Exception as e:
        print(e)
    
sg_control()
#while True:
#    h = int(datetime.now().strftime("%H"))
#    if (h==0) or (h==8) or (h==21):
#        sg_control() 
#        print (datetime.now().strftime("%m-%d-%Y %H:%M:%S"), " : wait 120 minutes.")
#        time.sleep(7200)
#    else:
#        print (datetime.now().strftime("%m-%d-%Y %H:%M:%S"), " : wait 20 minutes.")
#        time.sleep(1200)
