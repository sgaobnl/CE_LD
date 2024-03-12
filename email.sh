#!/bin/bash

lastfilepath=`find /scratch_local/SBND_Installation/data/commissioning/LD_result/ -name 'LD*.png' -type f -printf "%T@ %p\n" | sort -n | cut -d' ' -f 2- | tail -n 1`
lastfile=`basename $lastfilepath`
#echo $lastfile
filepattern=`echo $lastfile | cut -d_ -f1-8`
#echo $filepattern

NUM_OF_FILE=0
while read i
do
    echo "$i"
    NUM_OF_FILE=$(( $NUM_OF_FILE+1 ))
    export file${NUM_OF_FILE}=`base64 --wrap 0 $i`
    export filename${NUM_OF_FILE}=$i
done < <(find /scratch_local/SBND_Installation/data/commissioning/LD_result/ -name "$filepattern*" -type f)

echo "Sending ${NUM_OF_FILE} images"

rmstimefile=/scratch_local/SBND_Installation/data/commissioning/LD_result/RMS_vs_Time.png
#echo "RMS vs Time: $rmstimefile"
export rmstime_base64=`base64 --wrap 0 $rmstimefile`
#export filename=`basename $rmsfile`
envsubst < email.eml | sendmail -t
