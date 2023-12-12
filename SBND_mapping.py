# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Author: GSS
Mail: gao.hillhill@gmail.com
Description: 
Created Time: 7/15/2016 11:47:39 AM
Last modified: 6/27/2023 12:45:54 AM
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


csv_fn = "./SBND_EAST_APA_mapping.csv"

tindexs = []
with open(csv_fn, 'r') as fp:
    for cl in fp:
        if "\n" in cl:
            cl = cl.replace("\n", "")
        tmp = cl.split(",")
        x = []
        for i in tmp:
            x.append(i.replace(" ", ""))
        tindexs.append(x)
tindexs = tindexs [1:]

top_femb = [
            [  0, "Y33"], [  1, "Y34"], [  2, "Y35"], [  3, "Y36"], [  4, "Y37"], [  5, "Y38"], [  6, "Y39"], [  7, "Y40"],
            [  8, "Y41"], [  9, "Y42"], [ 10, "Y43"], [ 11, "Y44"], [ 12, "Y45"], [ 13, "Y46"], [ 14, "Y47"], [ 15, "Y48"],
            [ 16, "Y49"], [ 17, "Y50"], [ 18, "Y51"], [ 19, "Y52"], [ 20, "Y53"], [ 21, "Y54"], [ 22, "Y55"], [ 23, "Y56"],
            [ 24, "Y57"], [ 25, "Y58"], [ 26, "Y59"], [ 27, "Y60"], [ 28, "Y61"], [ 29, "Y62"], [ 30, "Y63"], [ 31, "Y64"],
            [ 32, "U16"], [ 33, "U15"], [ 34, "U14"], [ 35, "U13"], [ 36, "U12"], [ 37, "U11"], [ 38, "U10"], [ 39, "U09"],
            [ 40, "U08"], [ 41, "U07"], [ 42, "U06"], [ 43, "U05"], [ 44, "U04"], [ 45, "U03"], [ 46, "U02"], [ 47, "U01"],
            [ 48, "U32"], [ 49, "U31"], [ 50, "U30"], [ 51, "U29"], [ 52, "U28"], [ 53, "U27"], [ 54, "U26"], [ 55, "U25"],
            [ 56, "U24"], [ 57, "U23"], [ 58, "U22"], [ 59, "U21"], [ 60, "U20"], [ 61, "U19"], [ 62, "U18"], [ 63, "U17"],
            [ 64, "Y17"], [ 65, "Y18"], [ 66, "Y19"], [ 67, "Y20"], [ 68, "Y21"], [ 69, "Y22"], [ 70, "Y23"], [ 71, "Y24"],
            [ 72, "Y25"], [ 73, "Y26"], [ 74, "Y27"], [ 75, "Y28"], [ 76, "Y29"], [ 77, "Y30"], [ 78, "Y31"], [ 79, "Y32"],
            [ 80, "Y01"], [ 81, "Y02"], [ 82, "Y03"], [ 83, "Y04"], [ 84, "Y05"], [ 85, "Y06"], [ 86, "Y07"], [ 87, "Y08"],
            [ 88, "Y09"], [ 89, "Y10"], [ 90, "Y11"], [ 91, "Y12"], [ 92, "Y13"], [ 93, "Y14"], [ 94, "Y15"], [ 95, "Y16"],
            [ 96, "V32"], [ 97, "V31"], [ 98, "V30"], [ 99, "V29"], [100, "V28"], [101, "V27"], [102, "V26"], [103, "V25"],
            [104, "V24"], [105, "V23"], [106, "V22"], [107, "V21"], [108, "V20"], [109, "V19"], [110, "V18"], [111, "V17"],
            [112, "V16"], [113, "V15"], [114, "V14"], [115, "V13"], [116, "V12"], [117, "V11"], [118, "V10"], [119, "V09"],
            [120, "V08"], [121, "V07"], [122, "V06"], [123, "V05"], [124, "V04"], [125, "V03"], [126, "V02"], [127, "V01"]
           ]

side_femb = [
            [  0, "064"], [  1, "063"], [  2, "062"], [  3, "061"], [  4, "060"], [  5, "059"], [  6, "058"], [  7, "057"],
            [  8, "056"], [  9, "055"], [ 10, "054"], [ 11, "053"], [ 12, "052"], [ 13, "051"], [ 14, "050"], [ 15, "049"],
            [ 16, "048"], [ 17, "047"], [ 18, "046"], [ 19, "045"], [ 20, "044"], [ 21, "043"], [ 22, "042"], [ 23, "041"],
            [ 24, "040"], [ 25, "039"], [ 26, "038"], [ 27, "037"], [ 28, "036"], [ 29, "035"], [ 30, "034"], [ 31, "033"],
            [ 32, "016"], [ 33, "015"], [ 34, "014"], [ 35, "013"], [ 36, "012"], [ 37, "011"], [ 38, "010"], [ 39, "009"],
            [ 40, "008"], [ 41, "007"], [ 42, "006"], [ 43, "005"], [ 44, "004"], [ 45, "003"], [ 46, "002"], [ 47, "001"],
            [ 48, "032"], [ 49, "031"], [ 50, "030"], [ 51, "029"], [ 52, "028"], [ 53, "027"], [ 54, "026"], [ 55, "025"],
            [ 56, "024"], [ 57, "023"], [ 58, "022"], [ 59, "021"], [ 60, "020"], [ 61, "019"], [ 62, "018"], [ 63, "017"],
            [ 64, "080"], [ 65, "079"], [ 66, "078"], [ 67, "077"], [ 68, "076"], [ 69, "075"], [ 70, "074"], [ 71, "073"],
            [ 72, "072"], [ 73, "071"], [ 74, "070"], [ 75, "069"], [ 76, "068"], [ 77, "067"], [ 78, "066"], [ 79, "065"],
            [ 80, "096"], [ 81, "095"], [ 82, "094"], [ 83, "093"], [ 84, "092"], [ 85, "091"], [ 86, "090"], [ 87, "089"],
            [ 88, "088"], [ 89, "087"], [ 90, "086"], [ 91, "085"], [ 92, "084"], [ 93, "083"], [ 94, "082"], [ 95, "081"],
            [ 96, "128"], [ 97, "127"], [ 98, "126"], [ 99, "125"], [100, "124"], [101, "123"], [102, "122"], [103, "121"],
            [104, "120"], [105, "119"], [106, "118"], [107, "117"], [108, "116"], [109, "115"], [110, "114"], [111, "113"],
            [112, "112"], [113, "111"], [114, "110"], [115, "109"], [116, "108"], [117, "107"], [118, "106"], [119, "105"],
            [120, "104"], [121, "103"], [122, "102"], [123, "101"], [124, "100"], [125, "099"], [126, "098"], [127, "097"]
           ]

#sideu_femb = [
#            [  0, "U064"], [  1, "U063"], [  2, "U062"], [  3, "U061"], [  4, "U060"], [  5, "U059"], [  6, "U058"], [  7, "U057"],
#            [  8, "U056"], [  9, "U055"], [ 10, "U054"], [ 11, "U053"], [ 12, "U052"], [ 13, "U051"], [ 14, "U050"], [ 15, "U049"],
#            [ 16, "U048"], [ 17, "U047"], [ 18, "U046"], [ 19, "U045"], [ 20, "U044"], [ 21, "U043"], [ 22, "U042"], [ 23, "U041"],
#            [ 24, "U040"], [ 25, "U039"], [ 26, "U038"], [ 27, "U037"], [ 28, "U036"], [ 29, "U035"], [ 30, "U034"], [ 31, "U033"],
#            [ 32, "U016"], [ 33, "U015"], [ 34, "U014"], [ 35, "U013"], [ 36, "U012"], [ 37, "U011"], [ 38, "U010"], [ 39, "U009"],
#            [ 40, "U008"], [ 41, "U007"], [ 42, "U006"], [ 43, "U005"], [ 44, "U004"], [ 45, "U003"], [ 46, "U002"], [ 47, "U001"],
#            [ 48, "U032"], [ 49, "U031"], [ 50, "U030"], [ 51, "U029"], [ 52, "U028"], [ 53, "U027"], [ 54, "U026"], [ 55, "U025"],
#            [ 56, "U024"], [ 57, "U023"], [ 58, "U022"], [ 59, "U021"], [ 60, "U020"], [ 61, "U019"], [ 62, "U018"], [ 63, "U017"],
#            [ 64, "U080"], [ 65, "U079"], [ 66, "U078"], [ 67, "U077"], [ 68, "U076"], [ 69, "U075"], [ 70, "U074"], [ 71, "U073"],
#            [ 72, "U072"], [ 73, "U071"], [ 74, "U070"], [ 75, "U069"], [ 76, "U068"], [ 77, "U067"], [ 78, "U066"], [ 79, "U065"],
#            [ 80, "U096"], [ 81, "U095"], [ 82, "U094"], [ 83, "U093"], [ 84, "U092"], [ 85, "U091"], [ 86, "U090"], [ 87, "U089"],
#            [ 88, "U088"], [ 89, "U087"], [ 90, "U086"], [ 91, "U085"], [ 92, "U084"], [ 93, "U083"], [ 94, "U082"], [ 95, "U081"],
#            [ 96, "U128"], [ 97, "U127"], [ 98, "U126"], [ 99, "U125"], [100, "U124"], [101, "U123"], [102, "U122"], [103, "U121"],
#            [104, "U120"], [105, "U119"], [106, "U118"], [107, "U117"], [108, "U116"], [109, "U115"], [110, "U114"], [111, "U113"],
#            [112, "U112"], [113, "U111"], [114, "U110"], [115, "U109"], [116, "U108"], [117, "U107"], [118, "U106"], [119, "U105"],
#            [120, "U104"], [121, "U103"], [122, "U102"], [123, "U101"], [124, "U100"], [125, "U099"], [126, "U098"], [127, "U097"]
#           ]
#
#
#sidev_femb = [ [  0, "V064"], [  1, "V063"], [  2, "V062"], [  3, "V061"], [  4, "V060"], [  5, "V059"], [  6, "V058"], [  7, "V057"],
#               [  8, "V056"], [  9, "V055"], [ 10, "V054"], [ 11, "V053"], [ 12, "V052"], [ 13, "V051"], [ 14, "V050"], [ 15, "V049"],
#               [ 16, "V048"], [ 17, "V047"], [ 18, "V046"], [ 19, "V045"], [ 20, "V044"], [ 21, "V043"], [ 22, "V042"], [ 23, "V041"],
#               [ 24, "V040"], [ 25, "V039"], [ 26, "V038"], [ 27, "V037"], [ 28, "V036"], [ 29, "V035"], [ 30, "V034"], [ 31, "V033"],
#               [ 32, "V016"], [ 33, "V015"], [ 34, "V014"], [ 35, "V013"], [ 36, "V012"], [ 37, "V011"], [ 38, "V010"], [ 39, "V009"],
#               [ 40, "V008"], [ 41, "V007"], [ 42, "V006"], [ 43, "V005"], [ 44, "V004"], [ 45, "V003"], [ 46, "V002"], [ 47, "V001"],
#               [ 48, "V032"], [ 49, "V031"], [ 50, "V030"], [ 51, "V029"], [ 52, "V028"], [ 53, "V027"], [ 54, "V026"], [ 55, "V025"],
#               [ 56, "V024"], [ 57, "V023"], [ 58, "V022"], [ 59, "V021"], [ 60, "V020"], [ 61, "V019"], [ 62, "V018"], [ 63, "V017"],
#               [ 64, "V080"], [ 65, "V079"], [ 66, "V078"], [ 67, "V077"], [ 68, "V076"], [ 69, "V075"], [ 70, "V074"], [ 71, "V073"],
#               [ 72, "V072"], [ 73, "V071"], [ 74, "V070"], [ 75, "V069"], [ 76, "V068"], [ 77, "V067"], [ 78, "V066"], [ 79, "V065"],
#               [ 80, "V096"], [ 81, "V095"], [ 82, "V094"], [ 83, "V093"], [ 84, "V092"], [ 85, "V091"], [ 86, "V090"], [ 87, "V089"],
#               [ 88, "V088"], [ 89, "V087"], [ 90, "V086"], [ 91, "V085"], [ 92, "V084"], [ 93, "V083"], [ 94, "V082"], [ 95, "V081"],
#               [ 96, "V128"], [ 97, "V127"], [ 98, "V126"], [ 99, "V125"], [100, "V124"], [101, "V123"], [102, "V122"], [103, "V121"],
#               [104, "V120"], [105, "V119"], [106, "V118"], [107, "V117"], [108, "V116"], [109, "V115"], [110, "V114"], [111, "V113"],
#               [112, "V112"], [113, "V111"], [114, "V110"], [115, "V109"], [116, "V108"], [117, "V107"], [118, "V106"], [119, "V105"],
#               [120, "V104"], [121, "V103"], [122, "V102"], [123, "V101"], [124, "V100"], [125, "V099"], [126, "V098"], [127, "V097"]
#           ]

dec_chn = []
for fi in range(len(tindexs)):
    femb =  tindexs[fi]
    print (femb)
    apaloc = tindexs[fi][0]
    cratestr= tindexs[fi][1]
    fembstr=  tindexs[fi][2]
    posstr =  tindexs[fi][3]
    wibstr = tindexs[fi][4]

    crateno = int(cratestr[5])
    if ("BB" in posstr) or ("AA" in posstr) :
        posno = int(posstr[2:])
    else:
        posno = int(posstr[1:])

    wibno = int(wibstr[3])
    wibfembno = int(wibstr[8])
    
    if posno <= 9: #side fembs for U plane
        for ch in range(128): 
            uch = int(side_femb[ch][1]) + (posno-1)*128
            tmp = copy.deepcopy(femb)
            tmp.append(crateno)
            tmp.append(wibno)
            tmp.append(wibfembno)
            tmp.append(ch)
            tmp.append("U")
            tmp.append(uch)
            dec_chn.append(tmp)
    elif posno >= 36:  #side fembs for V plane
        for ch in range(128): 
            vch = int(side_femb[ch][1]) + (posno-36)*128 + (13*32*2)
            tmp = copy.deepcopy(femb)
            tmp.append(crateno)
            tmp.append(wibno)
            tmp.append(wibfembno)
            tmp.append(ch)
            tmp.append("V")
            tmp.append(vch)
            print (tmp)

            dec_chn.append(tmp)
    else: #top femb
        for ch in range(128): 
            chstr = top_femb[ch][1]
            tmp = copy.deepcopy(femb)
            tmp.append(crateno)
            tmp.append(wibno)
            tmp.append(wibfembno)
            tmp.append(ch)
            if "U" in chstr:
                tmp.append("U")
                tmp.append(int(chstr[1:])+128*9+(posno-10)*32)
            elif "V" in chstr:
                tmp.append("V")
                tmp.append(int(chstr[1:])+(posno-10)*32)
            else: #Y plane
                tmp.append("Y")
                tmp.append(int(chstr[1:])+(posno-10)*64)
            dec_chn.append(tmp)

top_row = "APA,Crate,FEMB_SN,POSITION,WIB_CONNECTION,Crate_No,WIB_no,WIB_FEMB_LOC,FEMB_CH,Wire_type,Wire_No,"
print (len(dec_chn))

fn_map = "./SBND_mapping.csv"
with open (fn_map, 'w') as fp:
    fp.write( top_row + "\n")
    for x in dec_chn:
        fp.write(",".join(str(i) for i in x) +  "," + "\n")


