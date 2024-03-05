#!/usr/bin/env bash
while true
do
    echo "Run the top_ld.py"
    python ./top_ld.py #uncomment it to perform top_ld.py
    python ./SBND_APA_ANA_v2.py
    python ./SBND_RMS_vs_Time.py
    echo "Done, wait for 30 minutes for antoher data taking or terminate it."
    sleep 1800 #change to 30*60 for 30 minutes
done
