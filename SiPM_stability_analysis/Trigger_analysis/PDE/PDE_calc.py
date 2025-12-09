#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Combine PDE values from:

1) Trigger file:
   trigger_pde_calc.hdf5
   -> timestamp format: YYYY-MM-DD HH:MM:SS

2) Darkrate file:
   darkrate_peak_ratios.hdf5
   -> hour format: YYYY_MM_DD_HH_MM

MATCHING RULE:
 - Match by SiPM (channel)
 - Match by uFEMB
 - Match ONLY BY HOUR (0-23)
   (date / minute ignored)

FINAL VALUE:
    PDE = trigger.Result + darkrate.ln_amp_ratio

Output file:
    combined_pde_by_hour.hdf5
"""

import numpy as np
import h5py
import os
from datetime import datetime


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

trigger_file = "/data/disk1/koloina/CN/trigger_pde.hdf5"
darkrate_file = "/data/disk1/koloina/CN/darkrate_peak_ratios.hdf5"
output_file   = "/data/disk1/koloina/CN/combined_pde_by_hour_new.hdf5"


# ------------------------------------------------------------
# TIMESTAMP PARSERS
# ------------------------------------------------------------

def parse_trigger_ts(ts):
    """YYYY-MM-DD HH:MM:SS"""
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except:
        return None


def parse_darkrate_hour(ts):
    """YYYY_MM_DD_HH_MM"""
    try:
        return datetime.strptime(ts, "%Y_%m_%d_%H_%M")
    except:
        return None


# ------------------------------------------------------------
# LOAD DARKRATE INTO MEMORY
# ------------------------------------------------------------

def load_darkrate_map():

    darkrate_map = {}
    # Structure:
    # darkrate_map[sipm][ufemb][hour] = ln_amp_ratio

    with h5py.File(darkrate_file, "r") as fin:

        for sipm in fin:
            darkrate_map.setdefault(sipm, {})

            for ufemb in fin[sipm]:
                darkrate_map[sipm].setdefault(ufemb, {})

                for hour_grp in fin[sipm][ufemb]:

                    dt = parse_darkrate_hour(hour_grp)
                    if dt is None:
                        continue

                    if "ln_amp_ratio" not in fin[sipm][ufemb][hour_grp]:
                        continue

                    ln_amp_ratio = fin[sipm][ufemb][hour_grp]["ln_amp_ratio"][()]

                    darkrate_map[sipm][ufemb][dt.hour] = float(ln_amp_ratio)

    return darkrate_map


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():

    print("\nLoading darkrate ratios...")
    darkrate_map = load_darkrate_map()

    print("\nProcessing trigger PDE results...")

    with h5py.File(trigger_file, "r") as f_trig, \
         h5py.File(output_file, "w") as fout:

        fout.attrs["formula"] = "PDE = trigger.Result + darkrate.ln_amp_ratio"
        fout.attrs["matching"] = "Matched by SiPM + uFEMB + hour ONLY"

        for sipm in f_trig:

            if sipm not in darkrate_map:
                print(f"⚠ Skipping {sipm}: no darkrate data")
                continue

            sipm_out = fout.require_group(sipm)

            for ufemb in f_trig[sipm]:

                if ufemb not in darkrate_map[sipm]:
                    print(f"⚠ Skipping {sipm}/{ufemb}: no darkrate data")
                    continue

                ufemb_out = sipm_out.require_group(ufemb)

                available_hours = darkrate_map[sipm][ufemb]

                if not available_hours:
                    print(f"⚠ Skipping {sipm}/{ufemb}: empty darkrate hours")
                    continue

                for ts in f_trig[sipm][ufemb]:

                    dt = parse_trigger_ts(ts)
                    if dt is None:
                        continue

                    hour = dt.hour

                    if hour not in available_hours:
                        print(f"⚠ Missing darkrate for {sipm}/{ufemb} at hour {hour:02d}")
                        continue

                    trig_grp = f_trig[sipm][ufemb][ts]

                    if "Result" not in trig_grp:
                        continue

                    trigger_val = trig_grp["Result"][()][0]
                    darkrate_val = available_hours[hour]

                    pde_sum = trigger_val + darkrate_val

                    out_grp = ufemb_out.require_group(ts)
                    out_grp.create_dataset("trigger_result", data=trigger_val)
                    out_grp.create_dataset("darkrate_ln_amp_ratio", data=darkrate_val)
                    out_grp.create_dataset("pde_sum", data=pde_sum)
                    out_grp.attrs["matched_hour"] = hour

                    print(f"✔ {sipm}/{ufemb}/{ts} "
                          f"H={hour:02d}  "
                          f"{trigger_val:.4f} + {darkrate_val:.4f} = {pde_sum:.4f}")

    print("\n✅ Finished writing combined PDE file:")
    print("   ", output_file)


if __name__ == "__main__":
    main()
