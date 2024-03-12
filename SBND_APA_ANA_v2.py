# -*- coding: utf-8 -*-
"""
File Name: cls_femb_config.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 3/20/2019 4:50:34 PM
Last modified: Sun Mar 10 22:11:42 2024
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
import string
import time
from datetime import datetime
import struct
import codecs
#from cls_config import CLS_CONFIG
from raw_convertor import RAW_CONV
import pickle
from shutil import copyfile
import operator
from fft_chn import chn_rfft_psd
from regs_process import FEMBREG_Process 


def FEMB_CHK(fembdata, rms_f = False, fs="./"):
    RAW_C = RAW_CONV()
    chn_rmss = []
    chn_rmss_filtered = []
    chn_peds = []
    chn_pkps = []
    chn_pkns = []
    chn_waves = []
    chn_avg_waves = []

    for adata in fembdata:
        chn_data, feed_loc, chn_peakp, chn_peakn = RAW_C.raw_conv_peak(adata)
        for achn in range(len(chn_data)):
            achn_ped = []
            if (rms_f) or (len(feed_loc) == 0):
                achn_ped += chn_data[achn] 
            else:
                for af in range(len(feed_loc[0:-2])):
                    achn_ped += chn_data[achn][feed_loc[af]+100: feed_loc[af+1]-100 ] 
            maxloc = np.where(achn_ped == np.max(achn_ped))[0][0]
            if maxloc < 50:
                achn_ped_sub = achn_ped[50:]
            elif maxloc > len(achn_ped)-50:
                achn_ped_sub = achn_ped[0:-50]
            else:
                achn_ped_sub = achn_ped[0:maxloc-50] + achn_ped[maxloc+50:] 
            minloc = np.where(achn_ped == np.min(achn_ped))[0][0]
            if minloc < 50:
                achn_ped_sub2 = achn_ped_sub[50:]
            elif minloc > len(achn_ped_sub)-50:
                achn_ped_sub2 = achn_ped_sub[0:-50]
            else:
                achn_ped_sub2 = achn_ped_sub[0:maxloc-50] + achn_ped_sub[maxloc+50:] 

            arms = np.std(achn_ped)
            arms_2 = np.std(achn_ped_sub2)
            aped = int(np.mean(achn_ped))
            if chn_peakp != None:
                apeakp = int(np.mean(chn_peakp[achn]))
                apeakn = int(np.mean(chn_peakn[achn]))
            else:
                apeakp = np.max(achn_ped)
                apeakn = np.min(achn_ped)
            chn_rmss.append(arms)
            chn_rmss_filtered.append(arms_2)
            chn_peds.append(aped)
            chn_pkps.append(apeakp)
            chn_pkns.append(apeakn)
            #chn_waves.append( chn_data[achn][feed_loc[0]: feed_loc[1]] )
            #chn_waves.append( chn_data[achn] )
            #avg_cnt = len(feed_loc)-2

            #avg_wave = np.array(chn_data[achn][feed_loc[0]: feed_loc[0] + 100]) 
            #for i in range(1, avg_cnt,1):
            #    #avg_wave += np.array(chn_data[achn][feed_loc[i]: feed_loc[i+1]]) 
            #    avg_wave += np.array(chn_data[achn][feed_loc[i]: feed_loc[i]+100]) 
            #avg_wave = avg_wave/avg_cnt
            #chn_avg_waves.append(avg_wave)
    ana_err_code = ""
    rms_mean = np.mean(chn_rmss)

    for gi in range(8): 
        ped_mean = np.mean(chn_peds[gi*16 : (gi+1)*16])
        pkp_mean = np.mean(chn_pkps[gi*16 : (gi+1)*16])
        pkn_mean = np.mean(chn_pkns[gi*16 : (gi+1)*16])
        ped_thr= 30 

    result = (True, "pass-", [chn_rmss, chn_peds, chn_pkps, chn_pkns, chn_rmss_filtered])
#    FEMB_PLOT(result, fn=fs.replace(".bin", ".png"))
    return result


def FEMB_SUB_PLOT(ax, x, y, title, xlabel, ylabel, color='b', marker='.', atwinx=False, ylabel_twx = "", e=None):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    if (atwinx):
        ax.errorbar(x,y,e, marker=marker, color=color)
        y_min = int(np.min(y))-1000
        y_max = int(np.max(y))+1000
        ax.set_ylim([y_min, y_max])
        ax2 = ax.twinx()
        ax2.set_ylabel(ylabel_twx)
        ax2.set_ylim([int((y_min/16384.0)*2048), int((y_max/16384.0)*2048)])
    else:
        ax.plot(x,y, marker=marker, color=color)

def FEMB_PLOT(results, fn="./"):
    chn_rmss = results[2][0]
    chn_peds = results[2][1]
    chn_pkps = results[2][2]
    chn_pkns = results[2][3]
    chn_wfs =  results[2][4]

    import matplotlib.pyplot as plt
    ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=1, rowspan=1)
    ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 2), (0, 1), colspan=1, rowspan=1)
    ax4 = plt.subplot2grid((2, 2), (1, 1), colspan=1, rowspan=1)
    chns = range(len(chn_rmss))
    FEMB_SUB_PLOT(ax1, chns, chn_rmss, title="RMS Noise", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax2, chns, chn_peds, title="Pedestal", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
    FEMB_SUB_PLOT(ax3, chns, chn_pkps, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='r', marker='.')
    FEMB_SUB_PLOT(ax3, chns, chn_peds, title="Pedestal", xlabel="CH number", ylabel ="ADC / bin", color='b', marker='.')
    FEMB_SUB_PLOT(ax3, chns, chn_pkns, title="Pulse Amplitude", xlabel="CH number", ylabel ="ADC / bin", color='g', marker='.')
    for chni in range(128):
        ts = 100 if (len(chn_wfs[chni]) > 100) else len(chn_wfs[chni])
        x = (np.arange(ts)) * 0.5
        y = chn_wfs[chni][0:ts]
        FEMB_SUB_PLOT(ax4, x, y, title="Waveform Overlap", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C%d'%(chni%9))

 
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
#    fn = rawdir +  
    plt.savefig(fn)
#    plt.show()
    plt.close()

def SBND_MAP():
    fn_map = "./SBND_mapping.csv"
    dec_chn = []
    with open (fn_map, 'r') as fp:
        for cl in fp:
            if "\n" in cl:
                cl = cl.replace("\n", "")
            tmp = cl.split(",")
            x = []
            for i in tmp:
                x.append(i.replace(" ", ""))
            dec_chn.append(x)
    dec_chn = dec_chn[1:]
    return dec_chn

def SBND_ANA(rawdir, rms_f=False, rn="./result.ln"):
    fns = []
    for root, dirs, files in os.walk(rawdir):
        for fn in files:
            if ("WIB_" in fn) and ("FEMB_" in fn) and (".bin" in fn):
                wibloc = fn.find("FEMB_")
                crateno = int(fn[wibloc-2])
                ptbno = int(fn[wibloc-1])
                fembno = int(fn[wibloc+5])
                fns.append([crateno, ptbno, fembno, rawdir + fn])
        break
    
    dec_chn = SBND_MAP()
    lendec = len(dec_chn)
    for df in fns:
        print ("Analyze: ", df)
        crateno = df[0]
        wibno   = df[1]
        fembno  = df[2]
        with open (df[3], "rb") as fs:
            raw = pickle.load(fs)
        if len(raw) != 8:
            print ("Invalid monitoring data,discard...")
            return None
        results = FEMB_CHK(raw, rms_f=False, fs=df[3])
        chn_rmss = results[2][0]
        chn_peds = results[2][1]
        chn_pkps = results[2][2]
        chn_pkns = results[2][3]
        chn_rmss_filtered = results[2][4]
        #chn_wfs =  results[2][4]
        #chn_avgwfs =  results[2][5]
    
        for i in range(lendec):
            if (int(dec_chn[i][5]) == crateno) and (int(dec_chn[i][6]) == wibno ) and (int(dec_chn[i][7]) == fembno ) :
                decch = int(dec_chn[i][8])
                dec_chn[i].append(chn_rmss[decch])
                dec_chn[i].append(chn_peds[decch])
                dec_chn[i].append(chn_pkps[decch])
                dec_chn[i].append(chn_pkns[decch])
                dec_chn[i].append(chn_rmss_filtered[decch])
                #dec_chn[i].append((chn_wfs[decch]))
                #dec_chn[i].append((chn_avgwfs[decch]))
         
    result=dec_chn
    if len(result[0]) < 20:
        rawdatapath = rawdir 
        Dec_add_cfgs(rawdatapath, result, rn)
        #fechnregs = []
        #for cfgroot, cfgdirs, cfgfiles in os.walk(rawdatapath):
        #    for cfn in cfgfiles:
        #        if (".femb" in cfn[-5:]) and ("WIB_10_226_34_" in cfn) and ("FEMB_" in cfn):
        #            fechnregs += FEMBREG_Process(rawdatapath + cfn)
        #    break
        #for xi in range(len(result)):
        #    for ci in fechnregs:
        #        if (ci[1] == int(result[xi][5])) and (ci[2] ==  int(result[xi][6])) and (ci[3] == int(result[xi][7])) and (ci[4] == int(result[xi][8])) : 
        #            result[xi] +=  ci
        #            fechnregs.remove(ci)
        #            break

        #with open(rn, 'wb') as f:
        #    pickle.dump(result, f)

    #with open(rn, 'wb') as f:
    #    pickle.dump(dec_chn, f)
    #fr =rawdir + "test_results"+".csv" 
    #with open (fr, 'w') as fp:
    #    top_row = "APA,Crate,FEMB_SN,POSITION,WIB_CONNECTION,Crate_No,WIB_no,WIB_FEMB_LOC,FEMB_CH,Wire_type,Wire_No,,RMS Noise, Pedestal, Pulse_Pos_Peak, Pulse_Neg_Peak, RMS(filtered),"
    #    fp.write( top_row + "\n")
    #    for x in dec_chn:
    #        fp.write(",".join(str(i) for i in x[0:17]) +  "," + "\n")
    return result

def d_dec_plt(dec_chn, n=1):
    #n=63-11-46 "CFGINFO"
    #n=63-11-17 sts
    #n=63-11-17+1 snc
    #n=63-11-17+2 sg0
    #n=63-11-17+3 sg1
    #n=63-11-17+4 st0
    #n=63-11-17+5 st1
    #n=63-11-17+7 sdc
    #n=63-11-17+8 slkh
    #n=63-11-17+8 slkh
    #n=63-11-17+13 slk
    #n=63-11-17+14 sdacsw1
    #n=63-11-17+15 sdacsw2 
    #n=63-11-17+16 asicdac
    #n=63-11-31+0 fpgadac_v
    #n=63-11-31+2 pls_period
    #n=63-11-31+4 fpga_tp_en
    #n=63-11-31+5 asic_tp_en
    #n=63-11-31+9 femb_tst_sel
    #n=63-11-41+0 femb_clk_sel
    #n=63-11-41+1 femb_cmd_sel
    #n=63-11-41+4 tst_wfm_gen_mode
    
    euvals = []
    evvals = []
    eyvals = []
    wuvals = []
    wvvals = []
    wyvals = []

    for d in dec_chn:
#        print (len(d))
#        print (d[11+6])
#        print (d[11+63-11-31+0])
#        exit()
        wireno = int(d[10])
        if (len(d)>=16):
            wirev = d[11+n]
        else:
            wirev = -1
        if int (d[5]) > 2:
            if "U" in d[9]:
                euvals.append([wireno,wirev])
            if "V" in d[9]:
                evvals.append([wireno,wirev])
            if "Y" in d[9]:
                eyvals.append([wireno,wirev])
        else:
            if "U" in d[9]:
                wuvals.append([wireno,wirev])
            if "V" in d[9]:
                wvvals.append([wireno,wirev])
            if "Y" in d[9]:
                wyvals.append([wireno,wirev])

    return euvals, evvals, eyvals, wuvals, wvvals, wyvals

def DIS_CFG_PLOT(dec_chn, fdir ) :
    for i in range(len(dec_chn)):
        if len(dec_chn[i]) > 20:
            #fecfgs = dec_chn[i][-1]
            fembcfgs = dec_chn[i][-5]
            wibcfgs = dec_chn[i][-6]

            sts = dec_chn[i][0-17]
            snc = dec_chn[i][1-17]
            sg0 = dec_chn[i][2-17]
            sg1 = dec_chn[i][3-17]
            st0 = dec_chn[i][4-17]
            st1 = dec_chn[i][5-17]
            smn = dec_chn[i][6-17]
            sdf = dec_chn[i][7-17]
            sdc = dec_chn[i][8-17]
            slkh = dec_chn[i][9-17]
            s16 = dec_chn[i][10-17]
            stb = dec_chn[i][11-17]
            stb1 = dec_chn[i][12-17]
            slk = dec_chn[i][13-17]
            sdacsw1 = dec_chn[i][14-17]
            sdacsw2 = dec_chn[i][15-17]
            sdac = dec_chn[i][16-17]

            fpgadac_v = dec_chn[i][0-31]
            pls_dly = dec_chn[i][1-31]
            pls_period = dec_chn[i][2-31]
            sys_clk_flg = dec_chn[i][3-31]
            fpga_tp_en = dec_chn[i][4-31]
            asic_tp_en = dec_chn[i][5-31]
            dac_sel = dec_chn[i][6-31]
            int_tp_en = dec_chn[i][7-31]
            ext_tp_en  = dec_chn[i][8-31]
            femb_tst_sel = dec_chn[i][9-31]
            pls_width = dec_chn[i][10-31]

            femb_clk_sel = dec_chn[i][0-41]
            femb_cmd_sel = dec_chn[i][1-41]
            femb_int_clk_sel = dec_chn[i][2-41]
            pwr_en = dec_chn[i][3-41]
            tst_wfm_gen_mode = dec_chn[i][4-41]
            si5344_lol = dec_chn[i][5-41]
            si5344_losxaxb = dec_chn[i][6-41]
            udp_pkg_size = dec_chn[i][7-41]
            link_sync_stat = dec_chn[i][8-41]
            eq_los_rx = dec_chn[i][9-41]

            #print (sdf, sdac, sg0, sg1, sts, pls_period, hex(pls_width), hex(udp_pkg_size))
            #exit()

            if sts == 1:
                if (sdacsw1 == 1) and (fpga_tp_en == 1):
                    calimode = "FPGADAC_0x%x"%fpgadac_v
                elif (sdacsw2 == 1) and (asic_tp_en == 1):
                    calimode = "ASICDAC_0x%x"%sdac
                elif (sdacsw1 == 0) and (sdacsw2 == 0):
                    calimode = "NoCali"
                else:
                    calimode = "Undef"
            else:
                calimode = "Noise"

            if sg0 ==0 and sg1 == 0: 
                gain = "4.7 mV/fC"
            elif sg0 ==1 and sg1 == 0: 
                gain = "7.8 mV/fC"
            elif sg0 ==0 and sg1 == 1: 
                gain = "14 mV/fC"
            elif sg0 ==1 and sg1 == 1: 
                gain = "25 mV/fC"

            if st0 ==0 and st1 == 0: 
                st = "1.0 $\mu$s"
            elif st0 ==1 and st1 == 0: 
                st = "0.5 $\mu$s"
            elif st0 ==0 and st1 == 1: 
                st = "3.0 $\mu$s"
            elif st0 ==1 and st1 == 1: 
                st = "2.0 $\mu$s"
                
            if femb_tst_sel == 0:
                datamode = "Detector"
            elif femb_tst_sel == 1:
                datamode = "Test Pattern"
            elif femb_tst_sel == 2:
                datamode = "Fake Waveform"
            elif femb_tst_sel == 3:
                datamode = "Chn_Map"
            else:
                datamode = "Undef"

            if tst_wfm_gen_mode == 0:
                wibdatamode = "FromFEMB"
            elif tst_wfm_gen_mode == 1:
                wibdatamode = "From_WIB_Sawtooth"
            elif tst_wfm_gen_mode == 2:
                wibdatamode = "From_WIB_CHN_MAP"
            else:
                wibdatamode = "Undef"
            break
        else:
            wibdatamode = "Invalid"
            datamode = "Invalid"
            calimode = "Invalid"
            gain = "Unknown"
            st = "Unknown"
    
    fn = fdir.split("/")[-1]
    if  (".ld" in fn[-3:]):
        logdate=fn[3:3+19]
        datex = datetime.strptime(logdate,'%Y_%m_%d_%H_%M_%S')
        ttime = datex.timestamp()    

    #print ( [ttime, wibdatamode, datamode, calimode, gain, st])
    return [ttime, wibdatamode, datamode, calimode, gain, st]

   
def DIS_PLOT(dec_chn, fdir, title = "RMS Noise Distribution", fn = "SBND_APA_RMS_DIS.png", ns=[5],  ylim=[-2,10], ylabel = "RMS / bit", note = ""):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12,6))
    plt.rcParams.update({'font.size': 12})
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)

    ax1.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    ax1.text(1000, -1, "U", color='b')
    ax1.text(3000, -1, "V", color='g')
    ax1.text(5000, -1, "Y", color='r')
    if len(note) != 0:
        ax1.text(100, ylim[1]*0.8, note )
        ax2.text(100, ylim[1]*0.8, note )
    ax1.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
    ax2.vlines(1984, 0, 4000, linestyles='dashed',color='k')
    ax2.vlines(1984*2, 0, 4000, linestyles='dashed',color='k')
    ax2.text(1000, -1, "U", color='b')
    ax2.text(3000, -1, "V", color='g')
    ax2.text(5000, -1, "Y", color='r')


    plot_info = DIS_CFG_PLOT(dec_chn, fdir ) 
    for n in ns:
        euvals, evvals, eyvals, wuvals, wvvals, wyvals = d_dec_plt(dec_chn, n=n)

        chns, vals=list(zip(*sorted(euvals, key=operator.itemgetter(0))))
        ax1.plot(chns, vals, color="C%d"%(n+1), marker='.', mfc='b', mec='b', label = "U" )
        chns, vals=list(zip(*sorted(wuvals, key=operator.itemgetter(0))))
        ax2.plot(chns, vals, color="C%d"%(n+1), marker='.', mfc='b', mec='b', label = "U" )

        chns, vals=list(zip(*sorted(evvals, key=operator.itemgetter(0))))
        ax1.plot(np.array(chns)+1984, vals, color="C%d"%(n+1), marker='.', mfc='g', mec='g',  label = "V" )
        chns, vals=list(zip(*sorted(wvvals, key=operator.itemgetter(0))))
        ax2.plot(np.array(chns)+1984, vals, color="C%d"%(n+1), marker='.', mfc='g', mec='g',  label = "V" )

        chns, vals=list(zip(*sorted(eyvals, key=operator.itemgetter(0))))
        ax1.plot(np.array(chns)+1984*2, vals, color="C%d"%(n+1), marker='.', mfc='r', mec='r',  label = "Y" )
        chns, vals=list(zip(*sorted(wyvals, key=operator.itemgetter(0))))
        ax2.plot(np.array(chns)+1984*2, vals, color="C%d"%(n+1), marker='.', mfc='r', mec='r',  label = "Y" )
    ax1.set_ylim((ylim))
    ax1.set_xlim((0,6000))
    ax1.set_ylabel (ylabel)
    ax1.set_xlabel ("Channel NO." + " (" + "Data_is_" + "_".join(plot_info[1:])+ ")")
#    ax1.text(100, ylim[1]*0.8, "Data_is_" + "_".join(plot_info[1:]))
    tstr = datetime.fromtimestamp(plot_info[0]).strftime("%Y-%m-%d %H:%M:%S")
    ax1.set_title ("EAST APA: " + title + " (" + tstr + ")")
#    ax1.legend()
    ax1.grid()

    ax2.set_ylim((ylim))
    ax2.set_xlim((0,6000))
    ax2.set_ylabel (ylabel)
    ax2.set_xlabel ("Channel NO."+ " (" + "Data_is_" + "_".join(plot_info[1:])+ ")")
#    ax2.text(100, ylim[1]*0.8, "Data_is_" + "_".join(plot_info[1:]))
    ax2.set_title ("WEST APA: " + title + " (" + tstr + ")")
#    ax2.legend()
    ax2.grid()

    ffig = fdir[0:-3] + fn 
    plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
    plt.savefig(ffig[0:-4] + ".png")
#    plt.savefig(ffig[0:-4] + ".svg")
#    plt.savefig(ffig[0:-4] + ".eps")
#    print ("result saves at {}".format(ffig))
    #plt.show()
    plt.close()


def DIS_CHN_PLOT(dec_chn, chnstr="U1"):
    apa = chnstr[0]
    wiretype = chnstr[1]
    wireno = int(chnstr[2:])
    for d in dec_chn:
        if (apa in d[0]) and (wiretype in d[9]) and (wireno == int(d[10])) and (len(d) >12):
            APA = d[0]
            Crate = d[1]
            FEMB_SN = d[2]
            POSITION = d[3]
            WIB_CONNECTION = d[4]
            Crate_No = d[5]
            WIB_no = d[6]
            WIB_FEMB_LOC = d[7]
            FEMB_CH = d[8]
            Wire_type = d[9]
            Wire_No = d[10]
            RMS = d[12]
            Pedmean = d[13]
            Plspp = d[14]
            Plsnp = d[15]
            wfs = d[16]
            avgwfs = d[17]
            import matplotlib.pyplot as plt

            fig = plt.figure(figsize=(8.5,8))
            fig.suptitle("Test Result of %s"%chnstr, weight ="bold", fontsize = 12)
            fig.text(0.10, 0.94-0.02, "APA: {}".format(APA)   )
            fig.text(0.55, 0.94-0.02, "Crate: {}".format(Crate)   )
            fig.text(0.10, 0.90-0.02, "FEMB SN: {}".format(FEMB_SN)   )
            fig.text(0.55, 0.90-0.02, "WIB CONNECTION: {}".format(WIB_CONNECTION)   )
            fig.text(0.10, 0.86-0.02, "Crate No: {}".format(Crate_No)   )
            fig.text(0.55, 0.86-0.02, "WIB No: {}".format(WIB_no)   )
            fig.text(0.10, 0.82-0.02, "WIB FEMB SLOT: {}".format(WIB_FEMB_LOC)   )
            fig.text(0.55, 0.82-0.02, "CHN on FEMB: {}".format(FEMB_CH)   )
            fig.text(0.10, 0.78-0.02, "Wire Type: {}".format(Wire_type)   )
            fig.text(0.55, 0.78-0.02, "Wire No.: {}".format(Wire_No)   )

            fig.text(0.10, 0.72-0.02, "RMS noise / bit: {:0.3f}".format(RMS), weight ="bold", color = 'b'  )
            fig.text(0.55, 0.72-0.02, "Pedestal / bit: {}".format(Pedmean) , weight ="bold", color = 'b'  )
            fig.text(0.10, 0.68-0.02, "Maximum Amplitude / bit: {}".format(Plspp) , weight ="bold", color = 'b'  )
            fig.text(0.55, 0.68-0.02, "Minmum Amplitude / bit: {}".format(Plsnp) , weight ="bold", color = 'b'  )

            ax1 = plt.subplot2grid((3, 2), (1, 0), colspan=1, rowspan=1)
            ax2 = plt.subplot2grid((3, 2), (2, 0), colspan=1, rowspan=1)
            ax3 = plt.subplot2grid((3, 2), (1, 1), colspan=1, rowspan=1)
            ax4 = plt.subplot2grid((3, 2), (2, 1), colspan=1, rowspan=1)

            if len(wfs) > 500:
                wlen = 500
            else:
                wlen = len(wfs)
            x = np.arange(wlen)
            y = wfs[0:wlen]
            FEMB_SUB_PLOT(ax1, x, y, title="Waveform", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C0')

            wlen = len(wfs)
            x = np.arange(wlen)
            y = wfs[0:wlen]
            FEMB_SUB_PLOT(ax2, x, y, title="Waveform", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C1')

            wlen = len(avgwfs)
            x = np.arange(wlen)
            y = avgwfs[0:wlen]
            FEMB_SUB_PLOT(ax3, x, y, title="Averaging Waveform", xlabel="Time / $\mu$s", ylabel="ADC /bin", color='C2')

            f,p = chn_rfft_psd(wfs,  fft_s = len(wfs), avg_cycle = 1)
            FEMB_SUB_PLOT(ax4, f, p, title="FFT ", xlabel="Frequency / Hz", ylabel=" / dB", color='C3')
            
            plt.tight_layout( rect=[0.05, 0.05, 0.95, 0.95])
            plt.show()
            #print ("result saves at {}".format(ffig))
            #plt.savefig(fn)
            plt.close()

def Dec_add_cfgs(rawdatapath, result, rn):
    fechnregs = []
    for cfgroot, cfgdirs, cfgfiles in os.walk(rawdatapath):
        for cfn in cfgfiles:
            if (".femb" in cfn[-5:]) and ("WIB_10_226_34_" in cfn) and ("FEMB_" in cfn):
                fechnregs += FEMBREG_Process(rawdatapath + cfn)
        break
    if len(fechnregs) == 0:
        print (rn, ">> No valid .femb file")
        return None
    for xi in range(len(result)):
        for ci in fechnregs:
            if (ci[1] == int(result[xi][5])) and (ci[2] ==  int(result[xi][6])) and (ci[3] == int(result[xi][7])) and (ci[4] == int(result[xi][8])) : 
                result[xi] +=  ci
                fechnregs.remove(ci)
                break
    with open(rn, 'wb') as f:
        pickle.dump(result, f)
    DIS_PLOTs(result, rn)


def DIS_PLOTs(result, rn):
    DIS_PLOT(dec_chn=result, fdir=rn, title = "RMS Noise Distribution", fn = "SBND_APA_RMS_DIS.png", ns=[5], ylim=[-2,8])
    DIS_PLOT(dec_chn=result, fdir=rn, title = "Pulse Response Distribution", fn = "SBND_APA_PLS_DIS.png", ns=[2,3,4], ylim=[-100,4000], ylabel="Amplitude / bit")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE TST (1:enable, 0:disable) distribution", fn = "SBND_APA_CFG_FE_TST_DIS.png", ns=[63-11-17], ylim=[-2,2], ylabel="FE_TST", note="1:EN, 0:DIS, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE SNC (Baseline) distribution", fn = "SBND_APA_CFG_FE_BL_DIS.png", ns=[63-11-17+1], ylim=[-2,2], ylabel="FE_BL", note="1:200mV, 0:900mV, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE SG0 (Gain0) distribution", fn = "SBND_APA_CFG_FE_SG0_DIS.png", ns=[63-11-17+2], ylim=[-2,2], ylabel="FE_Gain0", note="1:7.8 or 25, 0:4.7 or 14, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE SG1 (Gain1) distribution", fn = "SBND_APA_CFG_FE_SG1_DIS.png", ns=[63-11-17+3], ylim=[-2,2], ylabel="FE_Gain1", note="1:14 or 25, 0:4.7 or 7.8, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE ST0 (PeakTime0) distribution", fn = "SBND_APA_CFG_FE_ST0_DIS.png", ns=[63-11-17+4], ylim=[-2,2], ylabel="FE_ST0", note="1:0.5 or 2, 0:1 or 3, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE ST1 (PeakTime0) distribution", fn = "SBND_APA_CFG_FE_ST1_DIS.png", ns=[63-11-17+5], ylim=[-2,2], ylabel="FE_ST1", note="1:2 or 3, 0:0.5 or 1, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE SDF (Buf) distribution", fn = "SBND_APA_CFG_FE_SDF_DIS.png", ns=[63-11-17+7], ylim=[-2,2], ylabel="FE_BUF", note="1:ON, 0:OFF, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE SDACSW1 distribution", fn = "SBND_APA_CFG_FE_SDACSW1_DIS.png", ns=[63-11-17+14], ylim=[-2,2], ylabel="FE_TST_Src", note="0:Ext_dis , 0: Ext_en, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE SDACSW2 distribution", fn = "SBND_APA_CFG_FE_SDACSW1_DIS.png", ns=[63-11-17+15], ylim=[-2,2], ylabel="FE_TST_Src", note="0:Int_dis , 0: Int_en, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FE SDAC distribution", fn = "SBND_APA_CFG_FE_SDAC_DIS.png", ns=[63-11-17+16], ylim=[-2,78], ylabel="FE_DAC", note="0-3F: SDAC, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FPGA-DAC distribution", fn = "SBND_APA_CFG_FPGA_DAC_DIS.png", ns=[63-11-31+0], ylim=[-2,78], ylabel="FPGA_DAC", note="0-3F: FPGA-DAC, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "Pulse Period distribution", fn = "SBND_APA_CFG_PLS_Per_DIS.png", ns=[63-11-31+2], ylim=[-2,2000], ylabel="FPGA_Pls_Period", note=">0: Period, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FPGA_TP_EN distribution", fn = "SBND_APA_CFG_FPGA_TP_EN_DIS.png", ns=[63-11-31+4], ylim=[-2,2], ylabel="FPGA_TP_EN", note="1:en, 0:dis, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "ASIC_TP_EN distribution", fn = "SBND_APA_CFG_ASIC_TP_EN_DIS.png", ns=[63-11-31+5], ylim=[-2,2], ylabel="ASIC_TP_EN", note="1:en, 0:dis, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "FEMB data mode distribution", fn = "SBND_APA_CFG_FEMB_Data_Mode_DIS.png", ns=[63-11-31+9], ylim=[-2,6], ylabel="FEMB_Data_Mode", note="0:ADC, 1:TestPattern,2:Waveform, 3:CHN_Map, 4:Sawtooth, -1:Bad")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "WIB CLK distribution", fn = "SBND_APA_CFG_WIB_CLK_DIS.png", ns=[63-11-41+0], ylim=[-2,2], ylabel="WIB CLK SRC", note="0:OSC100MHz, 1:SI5344")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "WIB CMD distribution", fn = "SBND_APA_CFG_WIB_CMD_DIS.png", ns=[63-11-41+1], ylim=[-2,2], ylabel="WIB CMD SRC", note="0:WIB, 1:MBB")
    DIS_PLOT(dec_chn=result, fdir=rn, title = "WIB TST WFM distribution", fn = "SBND_APA_CFG_WIB_TST_WFM_DIS.png", ns=[63-11-41+4], ylim=[-2,4], ylabel="WIB TST WFM Mode", note="0:from FEMB, 1:Sawtooth,2:CHN-Map, -1:Bad")


#rawdir = """/Users/shanshangao/Downloads/SBND_LD/LD/"""
rawdir = """/scratch_local/SBND_Installation/data/commissioning/"""
#rawdir = """/scratch_local/SBND_Installation/data/commissioning/Varuna_LD/"""


result_dir = rawdir + "LD_result/"

d1ns = []
for root, dirs, files in os.walk(rawdir):
    for d1n in dirs:
        if ("2024_" in d1n) :
            d1ns.append(rawdir + d1n + "/")
    break

for d1n in d1ns:
    for root, dirs, files in os.walk(d1n):
        for d2n in dirs:
            if ("LD_2024_" in d2n) :
                anadir = d1n + d2n + "/"
                rn = result_dir + "/" + d2n + ".ld"
                pn = result_dir + "/" + d2n + "SBND_APA_CFG_FEMB_Data_Mode_DIS.png"
                if (os.path.isfile(pn)):
                    continue
                if (os.path.isfile(rn)):
                    if (int(d2n[8:10]) == 2) and (int(d2n[11:13])<16): #before 02/16, .femb and .wib save wrong data, dischard
                        continue 
                    with open(rn, 'rb') as f:
                        result = pickle.load(f)
                        flg = True
                        for x in result:
                            if len(x) > 20:
                                flg = False
                                break
                        if flg:
                            sub1dir = d2n[3:13]
                            sub2dir = d2n 
                            rawdatapath = result_dir + "/../" + sub1dir + "/" + sub2dir + "/"
                            fechnregs = []
                            Dec_add_cfgs(rawdatapath, result, rn)
                        else:
                            print ("Invalid, discard")
                            #pass
                            #DIS_PLOTs(result, rn)
                            continue
                else:
                    rms_f = False
                    result = SBND_ANA(anadir, rms_f = rms_f, rn=rn)
                    if result == None:
                        continue
                    else:
                        DIS_PLOTs(result, rn)

        break


#DIS_PLOT(dec_chn=result, fdir=rawdir, title = "Pulse Response Distribution", fn = "SBND_APA_PLS_DIS.png", ns=[2,3,4], ylim=[-100,4000], ylabel="Amplitude / bit")
#
#while True:
#    print ("Input a chnanel number following format (E/W)(U/V/Y)(Chn no.), e.g. EU0001")
#    xstr = input ("Input a channel number  > ")
#    if (len(xstr)>2) and (("E" in xstr[0]) or ("W" in xstr[0])) and (("U" in xstr[1]) or ("V" in xstr[1]) or ("Y" in xstr[1])):
#        try:
#            wno = int(xstr[2:])
#            DIS_CHN_PLOT(dec_chn=result, chnstr=xstr)
#        except ValueError:
#            print ("Wrong number, please input again")
#    else:
#        yns = input ("Exit Y/N")
#        if ("Y" in yns) or ("y" in yns):
#            exit()
#
    



    

