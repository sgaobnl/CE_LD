import os
import glob
from datetime import datetime
import pickle
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

current_year = str(datetime.now().year)

with open('/scratch_local/SBND_Installation/data/commissioning/LD_result/2025/LD_2025_01_07_11_17_16.deadchannels', 'rb') as file:
    defaultdcs = pickle.load(file)
#print(defaultdcs)

list_of_files = glob.glob('/scratch_local/SBND_Installation/data/commissioning/LD_result/'+current_year+'/'+'*deadchannels')
latest_file = max(list_of_files, key=os.path.getmtime)
#print(latest_file)
with open(latest_file, 'rb') as file:
    deadchannels = pickle.load(file)
#print(deadchannels)

strFrom = 'sbndwib'
#recipients = 'tjyang@fnal.gov'
#recipients = 'aaaaf37do5cye5svsdg3jj2rkm@shortbaseline.slack.com'
recipients = 'sbnd_cold_electronics-aaaamjjujebziez3xtqixfexxy@shortbaseline.slack.com, sbnd-shift-operations-aaaak3ro3cjdguez5l7glmobwu@shortbaseline.slack.com'
if deadchannels:
    message = MIMEMultipart()
    message['From'] = strFrom
    message['To'] = recipients
    message['Subject'] = f"{len(deadchannels)} dead channels, {len(deadchannels)-len(defaultdcs)} new dead channels"

    #body = f'The partition {partition} is {percent_used}% full.'
    #print(body)
    #print("Sending email")
    message.attach(MIMEText(latest_file+'\n', 'plain'))
    message.attach(MIMEText(', '.join(map(str,deadchannels)), 'plain'))
                   
    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(strFrom, recipients.split(','), message.as_string())
    smtp.quit()
