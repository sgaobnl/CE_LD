# -*- coding: utf-8 -*-
"""
File Name: cls_udp.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:52:43 PM
Last modified: 3/24/2025 10:58:32 AM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl

import struct
import sys 
import string
import socket
import time
import copy
from socket import AF_INET, SOCK_DGRAM
import codecs

class CLS_UDP:
    def write_reg(self, reg , data ):
        self.udp_port_update()
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
            return None
        dataVal = int(data)
        if (dataVal < 0) or (dataVal > self.MAX_REG_VAL):
            return None
        
        #crazy packet structure require for UDP interface
        dataValMSB = ((dataVal >> 16) & 0xFFFF)
        dataValLSB = dataVal & 0xFFFF
        WRITE_MESSAGE = struct.pack('HHHHHHHHH',socket.htons( self.KEY1  ), socket.htons( self.KEY2 ),socket.htons(regVal),socket.htons(dataValMSB),
                socket.htons(dataValLSB),socket.htons( self.FOOTER  ), 0x0, 0x0, 0x0  )
        
        #send packet to board, don't do any checks
        sock_write = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_write.setblocking(0)
        sock_write.sendto(WRITE_MESSAGE,(self.UDP_IP, self.UDP_PORT_WREG ))
        sock_write.close()

    def read_reg(self, reg ):
        self.udp_port_update()
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
                return -1

        #set up listening socket, do before sending read request
        sock_readresp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_readresp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_readresp.bind(('', self.UDP_PORT_RREGRESP ))
        sock_readresp.settimeout(2)

        #crazy packet structure require for UDP interface
        READ_MESSAGE = struct.pack('HHHHHHHHH',socket.htons(self.KEY1), socket.htons(self.KEY2),socket.htons(regVal),0,0,socket.htons(self.FOOTER),0,0,0)
        sock_read = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_read.setblocking(0)
        sock_read.sendto(READ_MESSAGE,(self.UDP_IP,self.UDP_PORT_RREG))
        sock_read.close()

        #try to receive response packet from board, store in hex
        data = []
        try:
                data = sock_readresp.recv(4*1024)
        except socket.timeout:
                sock_readresp.close()
                return -2        
        #dataHex = data.encode('hex')
        #dataHex = codecs.encode(bytes(data, 'utf-8'), 'hex')
        dataHex = codecs.encode(data, 'hex')
        sock_readresp.close()

        #extract register value from response
        if int(dataHex[0:4],16) != regVal :
                return -3
        dataHexVal = int(dataHex[4:12],16)
        return dataHexVal


    def write_reg_checked (self, reg , data ):
        i = 0
        while (i < 10 ):
            time.sleep(0.001)
            self.write_reg(reg , data )
            time.sleep(0.001)
            rdata = self.read_reg( reg)
            time.sleep(0.001)
            rdata = self.read_reg( reg)
            time.sleep(0.001)
            if (data == rdata ):
                break
            else:
                i = i + 1
                time.sleep(abs(i -1 + 0.001))
        if i >= 10 :
            print ("readback value is different from written data, %d, %x, %x"%(reg, data, rdata))
            sys.exit()

    def get_rawdata(self):
        #set up listening socket
        sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_data.bind(('', self.UDP_PORT_HSDATA))
        sock_data.settimeout(2)

        #receive data, don't pause if no response
        try:
            #data = sock_data.recv(8*1024)
            data = sock_data.recv(9014)
        except socket.timeout:
            print ("FEMB_UDP--> Error get_data: No data packet received from board, quitting")
            data = []
        sock_data.close()
        return data

    def get_rawdata_packets(self, val):
        numVal = int(val)
        #if (numVal < 0) or (numVal > self.MAX_NUM_PACKETS):
        if (numVal < 0) :
            print ("FEMB_UDP--> Error record_hs_data: Invalid number of data packets requested")
            return None

        try_n = 0
        timeout_cnt = 0
        defe_pkg_cnt = 0
        lost_pkg_fg  = True
        while ( lost_pkg_fg == True ):
            #set up listening socket
            sock_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
            sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#            sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000)
            sock_data.bind(('',self.UDP_PORT_HSDATA))
            sock_data.settimeout(3)
            #write N data packets to file
            #rawdataPackets = b""
            rawdataPackets = []
            for packet in range(0,numVal,1):
                data = None
                try:
                    data = sock_data.recv(8192)
                except socket.timeout:
                    if (timeout_cnt == 10):
                        sock_data.close()
                        print ("ERROR: UDP timeout, Please check if there is any conflict (someone else try to control WIB at the same time), continue anyway")
                        return None
                    else:
                        timeout_cnt = timeout_cnt + 1
                        print ("ERROR: UDP timeout,  Please check if there is any conflict, Try again in 3 seconds")
                        time.sleep(3)
                        continue
                if data != None :
                    #rawdataPackets += data
                    rawdataPackets.append(data)
            if len(rawdataPackets) != 0:
                rawdata = b''.join(rawdataPackets)
            sock_data.close()

            pkg_chk =  True
            if (pkg_chk):
                try_n = try_n + 1
                lost_pkg_fg = False
                #check data 
                #smps = len(rawdataPackets) / 2 / 16
                #dataNtuple =struct.unpack_from(">%dH"%(smps*16),rawdataPackets)
                smps = len(rawdata) / 2 / 16
                dataNtuple =struct.unpack_from(">%dH"%(smps*16),rawdata)
                if (self.jumbo_flag):
                    pkg_len = int(0x1E06/2)
                    pkg_len = int(0xcec)
                else:
                    pkg_len = int(0x406/2)
                pkg_index  = []
                datalength = int( (len(dataNtuple) // pkg_len) -3) * (pkg_len) 
                i = 0 
                while (i <= datalength ):
                    pkg_cnt0 =  ((dataNtuple[i+0]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1]& 0x00FFFFFFFF) + 0x00000001
                    pkg_cnt1 =  ((dataNtuple[i+0+pkg_len]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1+pkg_len]& 0x00FFFFFFFF)
                    acc_flag = (pkg_cnt0 == pkg_cnt1)
                    face_flg = ((dataNtuple[i+2+6] == 0xface) or (dataNtuple[i+2+6] == 0xfeed))
                    if (acc_flag == True) and (face_flg == True) :
                        pkg_index.append(i)
                        i = i + pkg_len
                    else:
                        print (pkg_cnt0, pkg_cnt1)
                        lost_pkg_fg = True
                        defe_pkg_cnt = defe_pkg_cnt + 1
                        break
                if (lost_pkg_fg == True):
                    if  (defe_pkg_cnt <10):
                        continue
                    else:
                        print ("Warning: defective packages in the %dth try were found!!!, try again"%defe_pkg_cnt)
                        pass
                else:
                    pass
                tmpa = pkg_index[0]
                tmpb = pkg_index[-1]
                data_a = ((dataNtuple[tmpa+0]<<16)&0x00FFFFFFFF) + (dataNtuple[tmpa+1]&0x00FFFFFFFF) 
                data_b = ((dataNtuple[tmpb+0]<<16)&0x00FFFFFFFF) + (dataNtuple[tmpb+1]&0x00FFFFFFFF) 
                if ( data_b > data_a ):
                    pkg_sum = data_b - data_a + 1
                else:
                    pkg_sum = (0x100000000 + data_b) - data_a + 1
                missed_pkgs = 0
                for i in range(len(pkg_index)-1):
                    tmpa = pkg_index[i]
                    tmpb = pkg_index[i+1]
                    data_a = ((dataNtuple[tmpa+0]<<16)&0x00FFFFFFFF) + (dataNtuple[tmpa+1]&0x00FFFFFFFF)
                    data_b = ((dataNtuple[tmpb+0]<<16)&0x00FFFFFFFF) + (dataNtuple[tmpb+1]&0x00FFFFFFFF) 
                    if ( data_b > data_a ):
                        add1 = data_b - data_a 
                    else:
                        add1 = (0x100000000 + data_b) - data_a 
                    missed_pkgs = missed_pkgs + add1 -1

                if (missed_pkgs > 0 ):
                    if (try_n > 8 ):
                        print ("Warning: UDP. missing udp pkgs = %d, total pkgs = %d "%(missed_pkgs, pkg_sum))
                        print ("Warning: UDP. missing %.8f%% udp packages"%(100.0*missed_pkgs/pkg_sum))
                    lost_pkg_fg = True
                else:
                    lost_pkg_fg = False

                if (try_n > 10 ):
                    print ("ERROR: defective packages or missing packages at 10th attempts, pass anyway")
                    lost_pkg_fg = False

            else:
                lost_pkg_fg = False
        return rawdataPackets

########################################################################################################

    def udp_port_update(self):
        self.UDP_PORT_WREG = 32000
        self.UDP_PORT_RREG = 32001
        self.UDP_PORT_RREGRESP = 32002
        self.UDP_PORT_HSDATA = 32003

    #__INIT__#
    def __init__(self):
        self.UDP_IP = "192.168.121.1"
        self.KEY1 = 0xDEAD
        self.KEY2 = 0xBEEF
        self.FOOTER = 0xFFFF
        self.MultiPort = False
        self.UDP_PORT_WREG = 32000
        self.UDP_PORT_RREG = 32001
        self.UDP_PORT_RREGRESP = 32002
        self.UDP_PORT_HSDATA = 32003
        self.MAX_REG_NUM = 0x666
        self.MAX_REG_VAL = 0xFFFFFFFF
        self.MAX_NUM_PACKETS = 1000000
        self.jumbo_flag = False

