# check disk usage and send email if 95% full.

import os
import glob
import psutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Define these once; use them twice!
strFrom = 'sbndwib'
#recipients = 'tjyang@fnal.gov'
#recipients = 'aaaaf37do5cye5svsdg3jj2rkm@shortbaseline.slack.com'
recipients = 'sbnd_cold_electronics-aaaamjjujebziez3xtqixfexxy@shortbaseline.slack.com, sbnd-shift-operations-aaaak3ro3cjdguez5l7glmobwu@shortbaseline.slack.com, tjyang@fnal.gov, sgao@bnl.gov, trj@fnal.gov'

# Define the partition to check 
partition = '/scratch_local' 

# Define the threshold (e.g., 95% full) 
threshold = 95

# Check disk usage
usage = psutil.disk_usage(partition)
percent_used = usage.percent

# Send email if the partition is full
if percent_used >= threshold:
    # Create the email content
    message = MIMEMultipart()
    message['From'] = strFrom
    message['To'] = recipients
    message['Subject'] = "Disk full"

    body = f'The partition {partition} is {percent_used}% full.'
    print(body)
    print("Sending email")
    message.attach(MIMEText(body, 'plain'))

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(strFrom, recipients.split(','), message.as_string())
    smtp.quit()
