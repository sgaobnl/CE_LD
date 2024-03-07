#!/bin/bash

rmsfile=`ls -Art /scratch_local/SBND_Installation/data/commissioning/LD_result/LD*png | tail -n 1`
echo "RMS file: $rmsfile"
export rms_base64=`base64 --wrap 0 $rmsfile`
rmstimefile=/scratch_local/SBND_Installation/data/commissioning/LD_result/RMS_vs_Time.png
echo "RMS vs Time: $rmstimefile"
export rmstime_base64=`base64 --wrap 0 $rmstimefile`
export filename=`basename $rmsfile`
envsubst < email.eml | sendmail -t
