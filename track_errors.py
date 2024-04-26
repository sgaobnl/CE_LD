import pickle
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.dates as md
import time
import datetime

date = sys.argv[1]
savedir = "/scratch_local/SBND_Installation/data/commissioning/"
savedir += date
savedir += "/LINK_STATUS"
#print(savedir)
wiblist = [11,12,13,14,15,16,21,22,23,24,25,26,31,32,33,34,35,36,41,42,43,44,45,46]
femblist = list(range(0,4))
linklist = list(range(0,4))
runs = os.listdir(savedir)
dataout = []
for run in runs:
    mydir = savedir + "/" + run + "/"
    files = os.listdir(mydir)
    for file in files:
        #print(mydir+file)
        f = open(mydir+file,'rb')
        data = pickle.load(f)
        f.close()
        for key in data:
            if ("CHK_ERR_LINK" in key):
                s1 = file.strip(".sts")
                time = s1[-19:]
                wibaddr = s1[9:21]
                nerr = data[key]
                #print("here: ", time, wibaddr)
                #print(key, " = ", data[key])
                info = [wibaddr, key, time, nerr]
                dataout.append(info)

for wib in wiblist:
    wibname = "10_226_34_"+str(wib)
    plt.figure()
    plt.axes()
    for femb in femblist:
        fembname = "FEMB"+str(femb)
        for link in linklist:
            linkname = "LINK"+str(link)
            px = []
            py = []
            for d in dataout:
                #print(d[0], wibname, fembname, linkname)
                if (wibname in d) and (fembname in d[1]) and (linkname in d[1]):
                    #print(wib, d)
                    timestr = d[2]
                    timevar = datetime.datetime.strptime(timestr,"%Y_%m_%d_%H_%M_%S")
                    timestamp = datetime.datetime.timestamp(timevar)
                    #print(timestamp)
                    nerr = d[3]
                    px.append(timevar)
                    py.append(nerr)
            label = fembname+"_"+linkname
            plt.plot(px,py,label=label,marker='x')
            print(wibname, fembname, linkname, py)
    plt.legend()
    ax=plt.gca()
    xfmt = md.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(xfmt)
    plt.title("CHECKSUM errors for WIB"+str(wib)+" on "+date)
    plt.savefig("errhist_"+date+"_wib"+str(wib)+".png")
    plt.close()

