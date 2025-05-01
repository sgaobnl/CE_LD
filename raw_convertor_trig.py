# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 4/9/2025 5:25:13 PM
"""

#defaut setting for scientific caculation
#import numpy
#import scipy
#from numpy import *
#import numpy as np
#import scipy as sp
#import pylab as pl
import numpy as np
import struct

class RAW_CONV():

    def raw_conv_per_trig(self, pkg_data, total_samN=140):

        chn_data=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
        udp_pkg_id =  0
        timestampes = 0
        ufemb_id = 0
        bad_pkg_flg = False
        #pkg_len = (((total_samN+1)*2)*13 + 8) *2
        #if len(pkg_data) != pkg_len :
        #    print ("wrong UDP pakage size, defective data likely")
        #    bad_pkg_flg = True
        #    return chn_data, timestampes, udp_pkg_id, ufemb_id
        #else:
        if True:
            dataNtuple =struct.unpack_from(">%dH"%(len(pkg_data)//2),pkg_data)

            udp_pkg_id =  ((dataNtuple[0]<<16)&0x0FFFFFFFF) + (dataNtuple[1]& 0x0FFFFFFFF) 

            timestampes = ((dataNtuple[2] << 48) &0xFFFF000000000000 ) + \
                          ((dataNtuple[3] << 32) &0x0000FFFF00000000 ) + \
                          ((dataNtuple[4] << 16) &0x00000000FFFF0000 ) + \
                          ((dataNtuple[5]      ) &0x000000000000FFFF )  

            sysstatus = ((dataNtuple[6] << 16) &0x0FFFF0000 ) + \
                        ((dataNtuple[7]      ) &0xFFFF )  
            if sysstatus == 0xfacebeef: #femb 0
                ufemb_id = 1
            elif sysstatus == 0xfacebee0: #femb1
                ufemb_id = 2
            else:
                udp_pkg_id =  0
                timestampes = 0
                ufemb_id = 0
                print ("warning defective UDP package likely")
                bad_pkg_flg = True

            if bad_pkg_flg:
                return chn_data, timestampes, udp_pkg_id, ufemb_id
            else:
                onepkgdata = dataNtuple
                i = 8
                while i < len(onepkgdata) :
                    if (onepkgdata[i]&0xf000 == 0xf000 ) or (onepkgdata[i]&0xe000 == 0xe000 )  :
                        if onepkgdata[i]&0x0100 == 0x0100:
                            a16 = 16
                        else:
                            a16 = 0
                        chn_data[a16 + 7].append( ((onepkgdata[i+1] & 0X0FFF)<<0 ))
                        chn_data[a16 + 6].append( ((onepkgdata[i+2] & 0X00FF)<<4)+ ((onepkgdata[i+1] & 0XF000) >> 12))
                        chn_data[a16 + 5].append( ((onepkgdata[i+3] & 0X000F)<<8) +((onepkgdata[i+2] & 0XFF00) >> 8 ))
                        chn_data[a16 + 4].append( ((onepkgdata[i+3] & 0XFFF0)>>4 ))
    
                        chn_data[a16 + 3].append( (onepkgdata[i+3+1] & 0X0FFF)<<0 )
                        chn_data[a16 + 2].append( ((onepkgdata[i+3+2] & 0X00FF)<<4) + ((onepkgdata[i+3+1] & 0XF000) >> 12))
                        chn_data[a16 + 1].append( ((onepkgdata[i+3+3] & 0X000F)<<8) + ((onepkgdata[i+3+2] & 0XFF00) >> 8 ))
                        chn_data[a16 + 0].append( ((onepkgdata[i+3+3] & 0XFFF0)>>4) )
    
                        chn_data[a16 + 15].append( ((onepkgdata[i+6+1] & 0X0FFF)<<0 ))
                        chn_data[a16 + 14].append( ((onepkgdata[i+6+2] & 0X00FF)<<4 )+ ((onepkgdata[i+6+1] & 0XF000) >> 12))
                        chn_data[a16 + 13].append( ((onepkgdata[i+6+3] & 0X000F)<<8 )+ ((onepkgdata[i+6+2] & 0XFF00) >> 8 ))
                        chn_data[a16 + 12].append( ((onepkgdata[i+6+3] & 0XFFF0)>>4 ))
    
                        chn_data[a16 + 11].append( ((onepkgdata[i+9+1] & 0X0FFF)<<0 ))
                        chn_data[a16 + 10].append( ((onepkgdata[i+9+2] & 0X00FF)<<4 )+ ((onepkgdata[i+9+1] & 0XF000) >> 12))
                        chn_data[a16 + 9].append(  ((onepkgdata[i+9+3] & 0X000F)<<8 )+ ((onepkgdata[i+9+2] & 0XFF00) >> 8 ))
                        chn_data[a16 + 8].append(  ((onepkgdata[i+9+3] & 0XFFF0)>>4 ))
                    else:
                        pass
                    i = i + 13 
                return chn_data, timestampes, udp_pkg_id, ufemb_id



    def __init__(self):
        self.jumbo_flag = True
   
#    def raw_conv_peak(self, raw_data):
#        chn_data, feed_loc = self.raw_conv_feedloc(raw_data)
#        if ( len(feed_loc)  ) > 2 :
#            chn_peakp=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],]
#            chn_peakn=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],]
#            for tmp in range(len(feed_loc)-1):
#                for chn in range(16):
#                    chn_peakp[chn].append ( np.max(chn_data[chn][feed_loc[ tmp]:feed_loc[tmp]+100 ]) )
#                    chn_peakn[chn].append ( np.min(chn_data[chn][feed_loc[ tmp]:feed_loc[tmp]+100 ]) )
#        else:
#            chn_peakp = None
#            chn_peakn = None
#        return  chn_data, feed_loc, chn_peakp, chn_peakn


#    def raw_conv_feedloc_trig(self, raw_data, total_samN=140):
#        smps = int(len(raw_data) //2)
#        dataNtuple =struct.unpack_from(">%dH"%(smps),raw_data)
#        if (self.jumbo_flag == True):
#            #pkg_len = int(0x1E06/2)
#            pkg_len = ((total_samN+1)*2)*13 + 8
#        else:
#            pkg_len = int(0x406/2)
#
#        chn_data=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
#        feed_loc=[]
#        pkg_index  = []
#        datalength = int( (len(dataNtuple) // pkg_len) -3) * (pkg_len) 
#    
#        i = int(0) 
#        k = []
#        j = int(0)
#        while (i <= datalength ):
#            data_a =  ((dataNtuple[i+0]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1]& 0x00FFFFFFFF) + 0x0000000001
#            data_b =  ((dataNtuple[i+0+pkg_len]<<16)&0x00FFFFFFFF) + (dataNtuple[i+1+pkg_len]& 0x00FFFFFFFF)
#            acc_flg = ( data_a  == data_b )
#            #face_flg = ((dataNtuple[i+2+6] == 0xface) or (dataNtuple[i+2+6] == 0xfeed))
#            face_flg = (dataNtuple[i+2+6]&0xf000 == 0xf000) 
#            if (face_flg == True ) and ( acc_flg == True ) :
#                pkg_index.append(i)
#                i = i + pkg_len
#            else:
#                i = i + 1 
#        #        k.append(i)
#    
#        #    if ( acc_flg == False ) :
#        #        j = j + 1
#        
#        #if ( len(k) != 0 ):
#        #    print ("raw_convertor.py: There are defective packages start at %d"%k[0] )
#        #if j != 0 :
#        #    print ("raw_convertor.py: drop %d packages"%(j) )
#    
#        tmpa = pkg_index[0]
#        tmpb = pkg_index[-1]
#        data_a = ((dataNtuple[tmpa+0]<<16)&0xFFFFFFFF) + (dataNtuple[tmpa+1]&0xFFFFFFFF) 
#        data_b = ((dataNtuple[tmpb+0]<<16)&0xFFFFFFFF) + (dataNtuple[tmpb+1]&0xFFFFFFFF) 
#        if ( data_b > data_a ):
#            pkg_sum = data_b - data_a + 1
#        else:
#            pkg_sum = (0x100000000 + data_b) - data_a + 1
#        missed_pkgs = 0
#        for i in range(len(pkg_index)-1):
#            tmpa = pkg_index[i]
#            tmpb = pkg_index[i+1]
#            data_a = ((dataNtuple[tmpa+0]<<16)&0xFFFFFFFF) + (dataNtuple[tmpa+1]&0xFFFFFFFF)
#            data_b = ((dataNtuple[tmpb+0]<<16)&0xFFFFFFFF) + (dataNtuple[tmpb+1]&0xFFFFFFFF) 
#            if ( data_b > data_a ):
#                add1 = data_b - data_a 
#            else:
#                add1 = (0x100000000 + data_b) - data_a 
#            missed_pkgs = missed_pkgs + add1 -1
#    
#        if (missed_pkgs > 0 ):
#            print ("raw_convertor.py: missing udp pkgs = %d, total pkgs = %d "%(missed_pkgs, pkg_sum) )
#            print ("raw_convertor.py: missing %.8f%% udp packages"%(100.0*missed_pkgs/pkg_sum) )
#        else:
#            pass
#    
#        smps_num = 0
#        for onepkg_index in pkg_index:
#            onepkgdata = dataNtuple[onepkg_index : onepkg_index + pkg_len]
#            i = 8
#            while i < len(onepkgdata) :
#                #if (onepkgdata[i] == 0xface ) or (onepkgdata[i] == 0xfeed ):
#                if (onepkgdata[i]&0xf000 == 0xf000 ) :
#                    if onepkgdata[i]&0x0100 == 1:
#                        a16 = 16
#                    else:
#                        a16 = 0
#                    chn_data[a16 + 7].append( ((onepkgdata[i+1] & 0X0FFF)<<0 ))
#                    chn_data[a16 + 6].append( ((onepkgdata[i+2] & 0X00FF)<<4)+ ((onepkgdata[i+1] & 0XF000) >> 12))
#                    chn_data[a16 + 5].append( ((onepkgdata[i+3] & 0X000F)<<8) +((onepkgdata[i+2] & 0XFF00) >> 8 ))
#                    chn_data[a16 + 4].append( ((onepkgdata[i+3] & 0XFFF0)>>4 ))
#    
#                    chn_data[a16 + 3].append( (onepkgdata[i+3+1] & 0X0FFF)<<0 )
#                    chn_data[a16 + 2].append( ((onepkgdata[i+3+2] & 0X00FF)<<4) + ((onepkgdata[i+3+1] & 0XF000) >> 12))
#                    chn_data[a16 + 1].append( ((onepkgdata[i+3+3] & 0X000F)<<8) + ((onepkgdata[i+3+2] & 0XFF00) >> 8 ))
#                    chn_data[a16 + 0].append( ((onepkgdata[i+3+3] & 0XFFF0)>>4) )
#    
#                    chn_data[a16 + 15].append( ((onepkgdata[i+6+1] & 0X0FFF)<<0 ))
#                    chn_data[a16 + 14].append( ((onepkgdata[i+6+2] & 0X00FF)<<4 )+ ((onepkgdata[i+6+1] & 0XF000) >> 12))
#                    chn_data[a16 + 13].append( ((onepkgdata[i+6+3] & 0X000F)<<8 )+ ((onepkgdata[i+6+2] & 0XFF00) >> 8 ))
#                    chn_data[a16 + 12].append( ((onepkgdata[i+6+3] & 0XFFF0)>>4 ))
#    
#                    chn_data[a16 + 11].append( ((onepkgdata[i+9+1] & 0X0FFF)<<0 ))
#                    chn_data[a16 + 10].append( ((onepkgdata[i+9+2] & 0X00FF)<<4 )+ ((onepkgdata[i+9+1] & 0XF000) >> 12))
#                    chn_data[a16 + 9].append(  ((onepkgdata[i+9+3] & 0X000F)<<8 )+ ((onepkgdata[i+9+2] & 0XFF00) >> 8 ))
#                    chn_data[a16 + 8].append(  ((onepkgdata[i+9+3] & 0XFFF0)>>4 ))
#                    #if (onepkgdata[i] == 0xfeed ):
#                    #    feed_loc.append(smps_num)
#                    #smps_num = smps_num + 1
#                else:
#                    pass
#                i = i + 13 
#        return chn_data, feed_loc
#           
