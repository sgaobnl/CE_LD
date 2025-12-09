#This code computes normalized resolution using gain2

import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime

# ----------------------------
# Paths
# ----------------------------
rootdir = "/data/disk1/koloina/waveform_fitting/Merge/"
hdf5_path = os.path.join(rootdir, "trig_Analysis.hdf5")
output_dir = os.path.join(rootdir, "normalized_resolution2_subplots")
os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Parameters
# ----------------------------
target_hours = [0, 8, 21]
colors = {0: "#084594", 8: "purple", 21: "black"}
labels = {0: "00h", 8: "08h", 21: "21h"}

# ----------------------------
# Collect per HV group
# ----------------------------
hv_groups = {"HV1": {}, "HV2": {}, "HV3": {}}

with h5py.File(hdf5_path, "r") as f:
    for sipm in f.keys():
        hv_prefix = next((hv for hv in hv_groups if hv in sipm), None)
        if hv_prefix is None:
            continue

        for ufemb in f[sipm].keys():
            time_list, res2_list, hour_list = [], [], []

            for date_str in sorted(f[sipm][ufemb].keys()):
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if dt.hour not in target_hours:
                    continue

                dset = f[sipm][ufemb][date_str]
                fitted_centers = np.array(dset["fitted_centers"])
                fwhms = np.array(dset["fwhms"])
                if len(fitted_centers) < 3 or len(fwhms) < 2:
                    continue

                gain2 = fitted_centers[2] - fitted_centers[1]
                if gain2 < 100:
                    gain2 = np.nan

                res2 = fwhms[1] * 100 / gain2 if not np.isnan(gain2) else np.nan
                if np.isnan(res2) or res2 < 0:
                    continue

                time_list.append(dt)
                hour_list.append(dt.hour)
                res2_list.append(res2)

            if len(time_list) == 0:
                continue

            # Sort data
            time_list, hour_list, res2_list = zip(*sorted(zip(time_list, hour_list, res2_list)))
            hours_since_start = [(t - time_list[0]).total_seconds() / 3600.0 for t in time_list]

            # Normalize Res2 per channel
            res2_arr = np.array(res2_list)
            res2_norm = res2_arr / np.nanmean(res2_arr)

            hv_groups[hv_prefix][sipm] = {
                "hours": np.array(hours_since_start),
                "hours_of_day": np.array(hour_list),
                "res2_norm": res2_norm,
            }

# ----------------------------
# Plot per HV group (18 subplots each)
# ----------------------------
for hv, channels in hv_groups.items():
    if len(channels) == 0:
        continue

    n_channels = len(channels)
    ncols = 6
    nrows = int(np.ceil(n_channels / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=(20, 10), sharex=True, sharey=True)
    axes = axes.flatten()

    for i, (sipm, data) in enumerate(channels.items()):
        ax = axes[i]
        for hr in target_hours:
            idx = np.where(data["hours_of_day"] == hr)[0]
            ax.plot(
                data["hours"][idx],
                data["res2_norm"][idx],
                "+-", markersize=3, color=colors[hr], label=f"{labels[hr]}" if i == 0 else ""
            )

        ax.set_title(sipm, fontsize=9)
        ax.grid(True, ls="--", alpha=0.5)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(0.1))
        ax.set_ylim(0.75, 1.25)

    # Remove unused axes
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(f"Normalized Resolution (Res2) per Channel - {hv}", fontsize=14)
    fig.text(0.5, 0.05, "Hours since start", ha="center")
    fig.text(0.06, 0.5, "Normalized Resolution (Res2 / mean)", va="center", rotation="vertical")

    plt.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.1, wspace=0.3, hspace=0.4)
    

    save_path = os.path.join(output_dir, f"{hv}_Normalized_Res2_subplots.png")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {save_path}")
