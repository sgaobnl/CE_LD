import pickle
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.dates as md
import time
import datetime

#So far checking for checksum errors: CHK_ERR_LINK
#Other keys to consider FRAME_ERR_LINK, TS_ERR_LINK

#Set start/end time and coincidence window
startstr = "2024_04_26_14_48_00"
endstr = "2024_04_26_15_00_00"
offset = 0.
timewindow = 15.

digitalnoisefile = "./digitalnoise_timeandplace_all.txt"
f = open(digitalnoisefile)
lines = f.readlines()
dginfo = []
for line in lines:
    if "Time" in line: continue
    if line == "\n": continue
    vals = line.split()
    info = []
    info.append(vals[0])
    dgwibval = vals[1]+vals[2]
    info.append(dgwibval)
    info.append(vals[3])
    info.append(vals[4])
    dginfo.append(info)
#print(dginfo)

date = "2024_04_26"
savedir = "/scratch_local/SBND_Installation/data/commissioning/"
savedir += date
savedir += "/LINK_STATUS"
runs = os.listdir(savedir)
dataout = []
for run in runs:
    mydir = savedir + "/" + run + "/"
    files = os.listdir(mydir)
    for file in files:
        f = open(mydir+file,'rb')
        data = pickle.load(f)
        f.close()
        for key in data:
            if ("CHK_ERR_LINK" in key or "FRAME_ERR_LINK" in key or "TS_ERR_LINK" in key):
                s1 = file.strip(".sts")
                time = s1[-19:]
                wibaddr = s1[9:21]
                nerr = data[key]
                keyout = wibaddr+"_"+key
                info = [keyout, time, nerr]
                dataout.append(info)
                if ("FRAME" in keyout and nerr>0): print("Got Frame error", keyout, time, nerr)
                if ("TS_ERR" in keyout and nerr>0): print("Got ts error", keyout, time, nerr)

channellistnerr = {}
channellisttimestamps = {}
#Go through the data to find new errors
dataout.sort(key=lambda x: x[1])
for d in dataout:
    key = d[0]
    time = d[1]
    nerr = d[2]
    if key not in channellistnerr.keys():
        channellistnerr[key] = nerr
        channellisttimestamps[key] = [time]
    else:
        if (nerr > channellistnerr[key]):
            channellistnerr[key] = nerr
            timelist = channellisttimestamps[key]
            timelist.append(time)            
            channellisttimestamps[key] = timelist

#print(channellistnerr.keys())
xstart = datetime.datetime.timestamp(datetime.datetime.strptime(startstr,"%Y_%m_%d_%H_%M_%S"))
xend = datetime.datetime.timestamp(datetime.datetime.strptime(endstr,"%Y_%m_%d_%H_%M_%S"))
t1 = [datetime.datetime.strptime(i,"%Y_%m_%d_%H_%M_%S") for i in channellisttimestamps["10_226_34_22_FEMB2_CHK_ERR_LINK0"]]
t2 = [datetime.datetime.strptime(i,"%Y_%m_%d_%H_%M_%S") for i in channellisttimestamps["10_226_34_22_FEMB2_CHK_ERR_LINK1"]]
t3 = [datetime.datetime.strptime(i,"%Y_%m_%d_%H_%M_%S") for i in channellisttimestamps["10_226_34_22_FEMB2_CHK_ERR_LINK2"]]
t4 = [datetime.datetime.strptime(i,"%Y_%m_%d_%H_%M_%S") for i in channellisttimestamps["10_226_34_22_FEMB2_CHK_ERR_LINK3"]]
tmpstamps = t1 + t2 + t3 + t4
plotstamps = [(datetime.datetime.timestamp(i) - xstart) for i in tmpstamps]
#print(plotstamps)
ny = len(plotstamps)
y = [1.]*ny
plt.figure()
plt.scatter(plotstamps,y,marker='.')
plt.tight_layout()
plt.xlim(0, 800)
plt.ylim(0.9,1.1)

#Search for matches between new errors and new digital noise
matchcount = 0
nomatchcount = 0
totalcount = 0

link0list = list(range(0,32))
link1list = list(range(32,64))
link2list = list(range(64,96))
link3list = list(range(96,128))


print(f"Skipping digital noise before {startstr} and after {endstr}...")
for info in dginfo:
    time = info[0]
    wib = info[1]
    femb = info[2]
    ch = info[3]
    dgtimestamp = datetime.datetime.fromtimestamp(int(time))
    dgtime  = dgtimestamp.strftime("%Y_%m_%d_%H_%M_%S")
    if ((float(time) < xstart) or (float(time) > xend)): 
        continue

    #if totalcount > 1000: break
    totalcount += 1
    foundmatch = False

    if int(ch) in link0list: link = "0"
    if int(ch) in link1list: link = "1"
    if int(ch) in link2list: link = "2"
    if int(ch) in link3list: link = "3"

    key = "10_226_34_"+wib+"_FEMB"+femb+"_CHK_ERR_LINK"+link

    if (key == "10_226_34_22_FEMB2_CHK_ERR"):
        plotstamp = float(time) - xstart
        plt.scatter(plotstamp,0.95,marker='.',color='r')

    cserrtimes = []
    if key in channellisttimestamps.keys():
        for t in channellisttimestamps[key]:
            cserrtimes.append(t)

    key = "10_226_34_"+wib+"_FEMB"+femb+"_FRAME_ERR_LINK"+link
    frerrtimes = []
    if key in channellisttimestamps.keys():
        for t in channellisttimestamps[key]:
            #print(t)
            frerrtimes.append(t)

    #print(cserrtimes)
    #print("***")
    #print(frerrtimes)
    alltimes = cserrtimes+frerrtimes
    #print("*****", key, dgtime, cserrtimes)
    #print("*****", totalcount, key, dgtime)
    for cstime in alltimes:
        cstimevar = datetime.datetime.strptime(cstime,"%Y_%m_%d_%H_%M_%S")
        cstime = datetime.datetime.timestamp(cstimevar)

        #if (abs(cstime-31-float(time)) < timewindow):
        if (abs(cstime+offset-float(time)) < timewindow):
            matchcount += 1
            foundmatch = True
            break
    if (not foundmatch):
        nomatchcount +=1

plt.savefig("timestamps.png")
plt.close()
total = matchcount + nomatchcount
print("If things have worked, these numbers are the same: ", total, totalcount)
print(f"Offset of {offset}s applied to timestamps")
print(f"Out of {totalcount} total digital noise entries, {matchcount} match to checksum or frame errors within {timewindow}s ")
print(f"Out of {totalcount} total digital noise entries, {nomatchcount} do no match to checksum or frame errors within {timewindow}s ")
