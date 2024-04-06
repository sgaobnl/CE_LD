# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.
import os
import glob
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Define these once; use them twice!
strFrom = 'sbnd'
#strTo = 'aaaaf37do5cye5svsdg3jj2rkm@shortbaseline.slack.com'
recipients = 'sbnd_cold_electronics-aaaamjjujebziez3xtqixfexxy@shortbaseline.slack.com'

# Create the root message and fill in the from, to, and subject headers
msgRoot = MIMEMultipart('related')
msgRoot['From'] = strFrom
#msgRoot['To'] = strTo
msgRoot.preamble = 'This is a multi-part message in MIME format.'

# Encapsulate the plain and HTML versions of the message body in an
# 'alternative' part, so message agents can decide which they want to display.
msgAlternative = MIMEMultipart('alternative')
msgRoot.attach(msgAlternative)

msgText = MIMEText('Noisy channels')
msgAlternative.attach(msgText)

list_of_files = glob.glob('/scratch_local/SBND_Installation/data/commissioning/LD_result/LD*WIB*FEMB*png')
latest_file = max(list_of_files, key=os.path.getmtime)
basename = os.path.basename(latest_file)
substr = basename[:basename.find("10_226_34")]
list_of_files = glob.glob('/scratch_local/SBND_Installation/data/commissioning/LD_result/'+substr+'*png')

for i in range(len(list_of_files)):
    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText('<img src="cid:image%d" width=1000><br>' % i, 'html')
    msgAlternative.attach(msgText)

    fp = open(list_of_files[i], 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image%d>' % i)
    msgRoot.attach(msgImage)

msgRoot['Subject'] = '%d noisy channels' % len(list_of_files)
if len(list_of_files) > 2:
    recipients = 'sbnd_cold_electronics-aaaamjjujebziez3xtqixfexxy@shortbaseline.slack.com,tjyang@fnal.gov,sgao@bnl.gov,meddage@ksu.edu,dmendezme@bnl.gov,mworcest@gmail.com,etw@bnl.gov'

# Send the email (this example assumes SMTP authentication is required)
msgRoot['To'] = recipients
import smtplib
smtp = smtplib.SMTP('localhost')
smtp.sendmail(strFrom, recipients.split(','), msgRoot.as_string())
smtp.quit()
