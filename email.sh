#!/bin/bash

rmsfile=`ls -Art /scratch_local/SBND_Installation/data/commissioning/LD_result/LD*png | tail -n 1`
export rms_base64=`cat $rmsfile | openssl base64`
rmstimefile=/scratch_local/SBND_Installation/data/commissioning/LD_result/RMS_vs_Time.png
export rmstime_base64=`cat $rmstimefile | openssl base64`
export filename=`basename $rmsfile`
envsubst < email.eml | sendmail -t
