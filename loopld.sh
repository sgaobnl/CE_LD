#!/usr/bin/env bash
while true
do
    echo "Run the top_ld.py"
    python ./top_ld.py #uncomment it to perform top_ld.py
    python ./SBND_APA_ANA_v2.py
    python ./SBND_RMS_vs_Time.py
#    ./email.sh
    python myemail.py
    python myemail2.py
    echo "Done, wait for 15 minutes for antoher data taking or terminate it."
    sleep 900 # run every 15 minutes
    #sleep 3600 #change to 60*60 for 60 minutes
    #sleep 300
done
