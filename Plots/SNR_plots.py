#----------------------------
Before use, run the code SiPm_trigger_data_analysis.py . You should get a .hdf5 file that contains the peaks data (centers, amplitudes, fwhm) , resolution, SNR and PDE.
#----------------------------

import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Paths
rootdir = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/SiPM"
hdf5_path = os.path.join(rootdir, "AnalysisResults.hdf5")
output_dir = os.path.join(rootdir, "SNR_plots")
os.makedirs(output_dir, exist_ok=True)

target_hours = [0, 8, 21]
colors = {0: "orange", 8: "purple", 21: "blue"}
labels = {0: "00h", 8: "08h", 21: "21h"}

def get_hour_from_datestr(datestr):
    dt = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
    return dt.hour

def get_day_number(datestr, ref_date):
    dt = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
    delta = dt - ref_date
    return delta.days + 1

with h5py.File(hdf5_path, "r") as f:
    channels = list(f.keys())
    all_dates = []
    for ch in channels:
        grp_ch = f[ch]
        for ufemb in grp_ch.keys():
            for date_str in grp_ch[ufemb].keys():
                all_dates.append(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S"))
    if not all_dates:
        print("No dates found in the HDF5 file.")
        exit(1)
    ref_date = min(all_dates)

    for ch in channels:
        plt.figure(figsize=(12, 6))
        grp_ch = f[ch]

        # snr_data: {hour: {day: snr}}
        snr_data = {h: {} for h in target_hours}

        for ufemb in grp_ch.keys():
            for date_str in grp_ch[ufemb].keys():
                dset = grp_ch[ufemb][date_str]
                snr_vals = dset.get("snr", None)
                if snr_vals is None or len(snr_vals) == 0:
                    continue
                snr = snr_vals[0]
                day = get_day_number(date_str, ref_date)
                hour = get_hour_from_datestr(date_str)

                if hour in target_hours:
                    if snr >= 100:
                        snr_data[hour][day] = np.nan
                    else:
                        snr_data[hour][day] = snr


        # Plot scatter points per hour
        for hour in target_hours:
            days = list(snr_data[hour].keys())
            snrs = [snr_data[hour][d] for d in days]
            if days:
                plt.scatter(days, snrs, label=labels[hour], color=colors[hour], alpha=0.7)

        # Draw vertical bars linking 00h, 08h, 21h points for the same day
        all_days = sorted(set().union(*[set(snr_data[h].keys()) for h in target_hours]))
        for day in all_days:
            points = []
            for h in target_hours:
                snr_val = snr_data[h].get(day, None)
                if snr_val is not None:
                    points.append((h, snr_val))
            if len(points) == len(target_hours):
                points.sort(key=lambda x: x[0])
                snr_vals = [p[1] for p in points]
                plt.vlines(day, min(snr_vals), max(snr_vals), colors='grey', alpha=0.5, linewidth=1)

        plt.title(f"SNR vs Day for Channel {ch}")
        plt.xlabel("Day")
        plt.ylabel("SNR")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        save_path = os.path.join(output_dir, f"SNR_{ch}.png")
        plt.savefig(save_path)
        plt.close()
        print(f"Saved plot: {save_path}")
