# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 6/27/2023 11:57:35 PM
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
import pickle

#rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/chk_post_bolt/"""
#rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/chk_pre_bolt/"""
#rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_SHV5V/"""

def result_rd(rawdir):
    chk_fns = []
    for root, dirs, files in os.walk(rawdir):
        for fn in files:
            if ".result" in fn:
                break
        break
    
    with open (rawdir + fn, "rb") as fs:
        result = pickle.load(fs)
        return result

def res_rms(result):
    euch    = np.arange(len(result[0][1])) + 1
    eurms   = result[0][1]
    evch    = np.arange(len(result[1][1])) + 1 + len(result[0][1])
    evrms   = result[1][1]
    eych    = np.arange(len(result[2][1])) + 1 + len(result[0][1]) + len(result[1][1])
    eyrms   = result[2][1]
    wuch    = np.arange(len(result[3][1])) + 1
    wurms   = result[3][1]
    wvch    = np.arange(len(result[4][1])) + 1 + len(result[3][1])
    wvrms   = result[4][1]
    wych    = np.arange(len(result[5][1])) + 1 + len(result[3][1]) + len(result[4][1])
    wyrms   = result[5][1]
    return euch , eurms, evch , evrms, eych , eyrms, wuch , wurms, wvch , wvrms, wych , wyrms 

def res_ped(result):
    euped   = result[0][2]
    evped   = result[1][2]
    eyped   = result[2][2]
    wuped   = result[3][2]
    wvped   = result[4][2]
    wyped   = result[5][2]
    return euped, evped, eyped, wuped, wvped, wyped 

def res_pkp(result):
    eupkp   = result[0][3]
    evpkp   = result[1][3]
    eypkp   = result[2][3]
    wupkp   = result[3][3]
    wvpkp   = result[4][3]
    wypkp   = result[5][3]
    return eupkp, evpkp, eypkp, wupkp, wvpkp, wypkp 

def res_pkn(result):
    eupkn   = result[0][4]
    evpkn   = result[1][4]
    eypkn   = result[2][4]
    wupkn   = result[3][4]
    wvpkn   = result[4][4]
    wypkn   = result[5][4]
    return eupkn, evpkn, eypkn, wupkn, wvpkn, wypkn 


#print (len(result2))

#rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_a_short/"""
#result1 = result_rd(rawdir)
#rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_a_coupling/"""
#result2 = result_rd(rawdir)
#rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/RMS20us/"""
#result3 = result_rd(rawdir)

#result = [
#            ["EU", e_urmss, e_upeds, e_upkps, e_upkns],
#            ["Ev", e_vrmss, e_vpeds, e_vpkps, e_vpkns],
#            ["EY", e_yrmss, e_ypeds, e_ypkps, e_ypkns],
#            ["WU", w_urmss, w_upeds, w_upkps, w_upkns],
#            ["Wv", w_vrmss, w_vpeds, w_vpkps, w_vpkns],
#            ["WY", w_yrmss, w_ypeds, w_ypkps, w_ypkns]
#         ]

#exit()

if False :   
    rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/chk_post_bolt/"""
    result1 = result_rd(rawdir)
    print (result1[0][1][1407-1], int(result1[0][1][1407-1]*193)) 
    print (result1[0][1][1411-1], int(result1[0][1][1411-1]*193)) 
    print (result1[2][1][426-1],  int(result1[2][1][426-1]*193 )) 
    print (result1[2][1][1239-1], int(result1[2][1][1239-1]*193)) 
    print (result1[4][1][953-1],  int(result1[4][1][953-1]*193 )) 
    print (result1[5][1][426-1],  int(result1[5][1][426-1]*193 )) 
    print (result1[5][1][1239-1], int(result1[5][1][1239-1]*193)) 


    euch , eurms, evch , evrms, eych , eyrms, wuch , wurms, wvch , wvrms, wych , wyrms = res_rms(result1)
#    import matplotlib.pyplot as plt
#    fig = plt.figure(figsize=(18,6))
#    plt.rcParams.update({'font.size': 18})
#    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
#    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
#    plt.plot(euch, np.array(eurms)*193, color='b', label = "U of East APA" )
#    plt.plot(evch, np.array(evrms)*193, color='g', label = "V of East APA" )
#    plt.plot(eych, np.array(eyrms)*193, color='r', label = "Y of East APA" )
#    plt.ylim((0,1000))
#    plt.xlim((0,6000))
#    plt.ylabel ("ENC /e-")
#    plt.xlabel ("Channel NO.")
#    plt.title ("ENC Distribution @ (14mV/fC, 2.0us)")
#    plt.legend()
#    plt.grid()
#    #    plt.plot(x, result2[i][1], color='r')
#    #    plt.plot(x, result3[i][1], color='g')
#    plt.show()
#    plt.close()
#
#   
#    import matplotlib.pyplot as plt
#    fig = plt.figure(figsize=(18,6))
#    plt.rcParams.update({'font.size': 18})
#    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
#    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
#    plt.plot(wuch, np.array(wurms)*193, color='b', label = "U of West APA" )
#    plt.plot(wvch, np.array(wvrms)*193, color='g', label = "V of West APA" )
#    plt.plot(wych, np.array(wyrms)*193, color='r', label = "Y of West APA" )
#    plt.ylim((0,1000))
#    plt.xlim((0,6500))
#    plt.title ("ENC Distribution @ (14mV/fC,  2.0$\mu$ss)")
#    plt.ylabel ("ENC /e-")
#    plt.xlabel ("Channel NO.")
#    plt.legend()
#    plt.grid()
#    #    plt.plot(x, result2[i][1], color='r')
#    #    plt.plot(x, result3[i][1], color='g')
#    plt.show()
#    plt.close()
#    exit()

   
    euped, evped, eyped, wuped, wvped, wyped = res_ped(result1)
    eupkp, evpkp, eypkp, wupkp, wvpkp, wypkp = res_pkp(result1)
    eupkn, evpkn, eypkn, wupkn, wvpkn, wypkn = res_pkn(result1)
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(18,6))
    plt.rcParams.update({'font.size': 18})
    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
    plt.plot(euch, np.array(euped), color='b', label = "East APA U" )
    plt.plot(evch, np.array(evped), color='g', label = "East APA V" )
    plt.plot(eych, np.array(eyped), color='r', label = "East APA Y" )
    plt.plot(euch, np.array(eupkp)+np.array(euped), color='b' )
    plt.plot(evch, np.array(evpkp)+np.array(evped), color='g' )
    plt.plot(eych, np.array(eypkp)+np.array(eyped), color='r' )
    plt.plot(euch, np.array(eupkn)+np.array(euped), color='b' )
    plt.plot(evch, np.array(evpkn)+np.array(evped), color='g' )
    plt.plot(eych, np.array(eypkn)+np.array(eyped), color='r' )

    plt.ylim((-100,4000))
    plt.xlim((0,6000))
    plt.ylabel ("ADC / bit")
    plt.xlabel ("Channel NO.")

    plt.title ("Pulse Response Distribution @ (14mV/fC, 2.0us)")
    plt.legend()
    plt.grid()
    plt.show()
    plt.close()
 
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(18,6))
    plt.rcParams.update({'font.size': 18})
    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
    plt.plot(wuch, np.array(wuped), color='b', label = "West APA U" )
    plt.plot(wvch, np.array(wvped), color='g', label = "West APA V" )
    plt.plot(wych, np.array(wyped), color='r', label = "West APA Y" )
    plt.plot(wuch, np.array(wupkp)+np.array(wuped), color='b' )
    plt.plot(wvch, np.array(wvpkp)+np.array(wvped), color='g' )
    plt.plot(wych, np.array(wypkp)+np.array(wyped), color='r' )
    plt.plot(wuch, np.array(wupkn)+np.array(wuped), color='b' )
    plt.plot(wvch, np.array(wvpkn)+np.array(wvped), color='g' )
    plt.plot(wych, np.array(wypkn)+np.array(wyped), color='r' )

    plt.ylim((-100,4000))
    plt.xlim((0,6000))
    plt.ylabel ("ADC / bit")
    plt.xlabel ("Channel NO.")
    plt.title ("Pulse Response Distribution @ (14mV/fC, 2.0us)")
    plt.legend()
    plt.grid()
    plt.show()
    plt.close()
   
#    import matplotlib.pyplot as plt
#    fig = plt.figure(figsize=(18,6))
#    plt.rcParams.update({'font.size': 18})
#    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
#    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
#    plt.plot(euch, np.array(eupkp)+np.array(euped), color='b', label = "U of East APA" )
#    plt.plot(evch, np.array(evpkp)+np.array(evped), color='g', label = "V of East APA" )
#    plt.plot(eych, np.array(eypkp)+np.array(eyped), color='r', label = "Y of East APA" )
#    plt.ylim((0,4000))
#    plt.xlim((0,6500))
#    plt.title ("Pulse Amplitude @ (14mV/fC, 2.0us)")
#    plt.legend()
#    plt.grid()
#    plt.show()
#    plt.close()

if False :   
    
    rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_noSHVcable/"""
    result1 = result_rd(rawdir)
    rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_SHVOFF/"""
    result2 = result_rd(rawdir)
    #print (len(result2))
    rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_SHV1V/"""
    result3 = result_rd(rawdir)
    rawdir = """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_west_apa_SHV5V/"""
    result4 = result_rd(rawdir)
    
    euch1 , eurms1, evch1 , evrms1, eych1 , eyrms1, wuch1 , wurms1, wvch1 , wvrms1, wych1 , wyrms1 = res_rms(result1)
    euch2 , eurms2, evch2 , evrms2, eych2 , eyrms2, wuch2 , wurms2, wvch2 , wvrms2, wych2 , wyrms2 = res_rms(result2)
    euch3 , eurms3, evch3 , evrms3, eych3 , eyrms3, wuch3 , wurms3, wvch3 , wvrms3, wych3 , wyrms3 = res_rms(result3)
    euch4 , eurms4, evch4 , evrms4, eych4 , eyrms4, wuch4 , wurms4, wvch4 , wvrms4, wych4 , wyrms4 = res_rms(result4)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(18,6))
    plt.rcParams.update({'font.size': 14})
    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')

#    plt.plot(wuch1, np.array(wurms1)*193, color='g', label = "West APA: No SHV Cable connected" )
#    plt.plot(wvch1, np.array(wvrms1)*193, color='g' )
#    plt.plot(wych1, np.array(wyrms1)*193, color='g' )
#    plt.plot(wuch2, np.array(wurms2)*193, color='b', label = "West APA: SHV Cable connected but HV off" )
#    plt.plot(wvch2, np.array(wvrms2)*193, color='b')
#    plt.plot(wych2, np.array(wyrms2)*193, color='b')
    plt.plot(wuch3, np.array(wurms3)*193, color='m', label = "West APA: SHV Cable connected HV set to 1V" )
    plt.plot(wvch3, np.array(wvrms3)*193, color='m' )
    plt.plot(wych3, np.array(wyrms3)*193, color='m' )
    plt.plot(wuch4, np.array(wurms4)*193, color='r', label = "West APA: SHV Cable connected HV set to 5V" )
    plt.plot(wvch4, np.array(wvrms4)*193, color='r' )
    plt.plot(wych4, np.array(wyrms4)*193, color='r' )
    plt.ylim((0,1000))
    plt.xlim((0,6000))
    plt.title ("Noise Distribution @ (14mV/fC, 2.0us)")
    plt.ylabel ("ENC /e-")
    plt.xlabel ("Channel NO.")

    plt.legend()
    plt.grid()
    #    plt.plot(x, result2[i][1], color='r')
    #    plt.plot(x, result3[i][1], color='g')
    plt.show()
    plt.close()


if False :   
    
    rawdir =  """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/RMS20us/"""
    result1 = result_rd(rawdir)
    rawdir =  """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/RMS20usHVoff/"""
    result2 = result_rd(rawdir)
    #print (len(result2))
    rawdir =  """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/RMS20usHV1V/"""
    result3 = result_rd(rawdir)
    
    euch1 , eurms1, evch1 , evrms1, eych1 , eyrms1, wuch1 , wurms1, wvch1 , wvrms1, wych1 , wyrms1 = res_rms(result1)
    euch2 , eurms2, evch2 , evrms2, eych2 , eyrms2, wuch2 , wurms2, wvch2 , wvrms2, wych2 , wyrms2 = res_rms(result2)
    euch3 , eurms3, evch3 , evrms3, eych3 , eyrms3, wuch3 , wurms3, wvch3 , wvrms3, wych3 , wyrms3 = res_rms(result3)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(18,6))
    plt.rcParams.update({'font.size': 14})
    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')

    plt.plot(euch1, np.array(eurms1)*193, color='g', label = "East APA: No SHV Cable connected" )
    plt.plot(evch1, np.array(evrms1)*193, color='g' )
    plt.plot(eych1, np.array(eyrms1)*193, color='g' )
#    plt.plot(euch2, np.array(eurms2)*193, color='b', label = "East APA: SHV Cable connected but HV off" )
#    plt.plot(evch2, np.array(evrms2)*193, color='b')
#    plt.plot(eych2, np.array(eyrms2)*193, color='b')
    plt.plot(euch3, np.array(eurms3)*193, color='m', label = "East APA: SHV Cable connected HV set to 1V" )
    plt.plot(evch3, np.array(evrms3)*193, color='m' )
    plt.plot(eych3, np.array(eyrms3)*193, color='m' )
    plt.ylim((0,1000))
    plt.xlim((0,6000))
    plt.title ("Noise Distribution @ (14mV/fC, 2.0us)")
    plt.ylabel ("ENC /e-")
    plt.xlabel ("Channel NO.")

    plt.legend()
    plt.grid()
    #    plt.plot(x, result2[i][1], color='r')
    #    plt.plot(x, result3[i][1], color='g')
    plt.show()
    plt.close()


if True :   
    
    rawdir =  """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/chk_post_bolt/"""
    rawdir =  """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0621/RMS20us/"""
    result1 = result_rd(rawdir)
    rawdir =  """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_a_short/"""
    result2 = result_rd(rawdir)
    #print (len(result2))
    rawdir =  """D:/OneDrive - Brookhaven National Laboratory/LArTPC/Test_Summary/SBND/SBND_Fermilab_Flange_Installation/SBND_Installation_Data/SBND/0622/noise_a_coupling/"""
    result3 = result_rd(rawdir)
    
    euch1 , eurms1, evch1 , evrms1, eych1 , eyrms1, wuch1 , wurms1, wvch1 , wvrms1, wych1 , wyrms1 = res_rms(result1)
    euch2 , eurms2, evch2 , evrms2, eych2 , eyrms2, wuch2 , wurms2, wvch2 , wvrms2, wych2 , wyrms2 = res_rms(result2)
    euch3 , eurms3, evch3 , evrms3, eych3 , eyrms3, wuch3 , wurms3, wvch3 , wvrms3, wych3 , wyrms3 = res_rms(result3)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(18,6))
    plt.rcParams.update({'font.size': 14})
    plt.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    plt.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')

    plt.plot(euch1, np.array(eurms1)*193, color='g', label = "East APA: ARAPUCA open" )
    plt.plot(evch1, np.array(evrms1)*193, color='g' )
    plt.plot(eych1, np.array(eyrms1)*193, color='g' )
#    plt.plot(euch2, np.array(eurms2)*193, color='b', label = "East APA: ARAPUCA short" )
#    plt.plot(evch2, np.array(evrms2)*193, color='b')
#    plt.plot(eych2, np.array(eyrms2)*193, color='b')
    plt.plot(euch3, np.array(eurms3)*193, color='m', label = "East APA: ARAPUCA with coupler" )
    plt.plot(evch3, np.array(evrms3)*193, color='m' )
    plt.plot(eych3, np.array(eyrms3)*193, color='m' )
    plt.ylim((0,1000))
    plt.xlim((0,6000))
    plt.title ("Noise Distribution @ (14mV/fC, 2.0us)")
    plt.ylabel ("ENC /e-")
    plt.xlabel ("Channel NO.")

    plt.legend()
    plt.grid()
    #    plt.plot(x, result2[i][1], color='r')
    #    plt.plot(x, result3[i][1], color='g')
    plt.show()
    plt.close()


