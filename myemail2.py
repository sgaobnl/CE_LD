import os
import time
import glob
import base64
import subprocess

list_of_files = glob.glob('/scratch_local/SBND_Installation/data/commissioning/LD_result/LD*_APA_CFG_*png')
latest_file = max(list_of_files, key=os.path.getmtime)
ts = os.path.getmtime(latest_file)
basename = os.path.basename(latest_file)
#print(basename)
substr = basename[:basename.find("SBND_APA_")]
list_of_files = glob.glob('/scratch_local/SBND_Installation/data/commissioning/LD_result/'+substr+'*SBND_APA_'+'*png')

list_of_files.insert(0, "/scratch_local/SBND_Installation/data/commissioning/LD_result/RMS_vs_Time.png")

with open(r'email.eml', 'r') as file: 
    data = file.read()

for i in range(len(list_of_files)):
    print(list_of_files[i])
    with open(list_of_files[i], "rb") as imagefile:
        convert = base64.b64encode(imagefile.read())
    #print(convert.decode('utf-8'))
    data = data.replace("{filename%d}"%i, os.path.basename(list_of_files[i]))
    data = data.replace("{file%d}"%i, convert.decode('utf-8'))
#    os.environ['file%d'%i] = convert.decode('utf-8')
#    os.environ['filename%d'%i] = os.path.basename(list_of_files[i])

data = data.replace("TimeStamp", time.ctime(ts)+", dt = %.1f hrs" % ((time.time() - ts)/3600))

with open(r'finalemail.eml', 'w') as file: 
  
    # Writing the replaced data in our 
    # text file 
    file.write(data) 

#subprocess.Popen('echo "Geeks 4 Geeks"', shell=True)
#subprocess.Popen("envsubst < email.eml > test" , shell=True)
subprocess.Popen("sendmail -t < finalemail.eml", shell=True)
subprocess.Popen("rm -f finalemail.eml", shell=True)
