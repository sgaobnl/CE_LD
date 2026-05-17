import os
import time
import glob
import base64
import subprocess
from datetime import datetime

current_year = str(datetime.now().year)

list_of_files = glob.glob('/scratch_local/SBND_Installation/data/commissioning/LD_result/'+current_year+'/'+'LD*_APA_CFG_*png')
latest_file = max(list_of_files, key=os.path.getmtime)
ts = os.path.getmtime(latest_file)
basename = os.path.basename(latest_file)
#print(basename)
substr = basename[:basename.find("SBND_APA_")]
list_of_files = glob.glob('/scratch_local/SBND_Installation/data/commissioning/LD_result/'+current_year+'/'+substr+'*SBND_APA_'+'*png')
list_of_files.sort(reverse=True)

list_of_files.insert(0, "/scratch_local/SBND_Installation/data/commissioning/LD_result/RMS_vs_Time.png")

with open(r'emailtrj3.eml', 'r') as file: 
    data = file.read()

# make a single PDF file

subprocess.run(["convert"] + list_of_files + ["plots.pdf"], check=True)

with open("plots.pdf","rb") as imagefile:
    convert = base64.b64encode(imagefile.read())   
    data = data.replace("{file0}", convert.decode('utf-8'))

data = data.replace("TimeStamp", time.ctime(ts)+", dt = %.1f hrs" % ((time.time() - ts)/3600))

with open(r'finalemail.eml', 'w') as file:
    file.write(data)
process = subprocess.Popen("sendmail -t < finalemail.eml", shell=True)
exit_code = process.wait()
subprocess.Popen("rm -f finalemail.eml", shell=True)
subprocess.Popen("rm -f plots.pdf", shell=True)
