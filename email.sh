#!/bin/bash

lastfilepath=`find /scratch_local/SBND_Installation/data/commissioning/LD_result/ -name 'LD*.png' -type f -printf "%T@ %p\n" | sort -n | cut -d' ' -f 2- | tail -n 1`
lastfile=`basename $lastfilepath`
#echo $lastfile
filepattern=`echo $lastfile | cut -d_ -f1-8`
#echo $filepattern

rmstimefile=/scratch_local/SBND_Installation/data/commissioning/LD_result/RMS_vs_Time.png
export rmstime_base64=`base64 --wrap 0 $rmstimefile`
echo $rmstimefile

NUM_OF_FILE=1
while read i
do
    echo "$i"
    export file${NUM_OF_FILE}=`base64 --wrap 0 $i`
    export filename${NUM_OF_FILE}=`basename $i`
    NUM_OF_FILE=$(( $NUM_OF_FILE+1 ))
done < <(find /scratch_local/SBND_Installation/data/commissioning/LD_result/ -name "$filepattern*" -type f | sort -r)

echo "Sending ${NUM_OF_FILE} images"

envsubst < email.eml | sendmail -t
