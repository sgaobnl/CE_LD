#!/usr/bin/env bash
nap_time=900 # in seconds
#nap_time=120 # in seconds
while true
do
    # one CE monitoring plots
    echo "Run top_ld.py"
    python ./top_ld.py
    python ./SBND_APA_ANA_v2.py
    python ./SBND_RMS_vs_Time.py
    #./email.sh
    python myemail.py
    python myemail2.py
    echo "Done, wait for $nap_time seconds"
    sleep $nap_time
    # 5 checksum error points
    echo "Run top_link_stats.py"
    python ./top_link_stats.py
    echo "Done, wait for $nap_time seconds"
    sleep $nap_time
    echo "Run top_link_stats.py"
    python ./top_link_stats.py
    echo "Done, wait for $nap_time seconds"
    sleep $nap_time
    echo "Run top_link_stats.py"
    python ./top_link_stats.py
    echo "Done, wait for $nap_time seconds"
    sleep $nap_time
    echo "Run top_link_stats.py"
    python ./top_link_stats.py
    echo "Done, wait for $nap_time seconds"
    sleep $nap_time
    echo "Run top_link_stats.py"
    python ./top_link_stats.py
    echo "Done"
done
