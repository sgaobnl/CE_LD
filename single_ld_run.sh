#!/usr/bin/env bash
echo "Running the top_ld.py"
python ./top_ld.py
python ./SBND_APA_ANA_v2.py
python ./SBND_RMS_vs_Time.py
python myemail.py
python myemail2.py
echo "Done!"
