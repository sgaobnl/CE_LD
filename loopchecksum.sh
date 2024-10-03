#!/usr/bin/env bash
nap_time=120
while true
do
    echo "Run the top_link_stats.py"
    python ./top_link_stats.py
    echo "Done, wait for $nap_time seconds"
    sleep $nap_time
done
