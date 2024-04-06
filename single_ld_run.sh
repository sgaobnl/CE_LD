#!/usr/bin/env bash
echo "Running the top_ld.py"
python ./top_ld.py
python ./SBND_APA_ANA_v2.py
python ./SBND_RMS_vs_Time.py
./email.sh
echo "Done!"
