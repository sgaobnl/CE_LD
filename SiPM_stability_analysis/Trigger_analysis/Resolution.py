#!/usr/bin/env python3
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime
import re

# ----------------------------
# Paths
# ----------------------------
rootdir = "/data/disk1/koloina/waveform_fitting/SIPM/Final_plots/"
hdf5_path = os.path.join(rootdir, "LED_Analysis_Final.hdf5")
output_dir = os.path.join(rootdir, "Res_plots")
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

        # ✅ CORRECT CHANNEL PARSING
        match = re.search(r"CH(\d+)", sipm)
        if not match:
            continue
        chan = match.group(1)   # "05", "15", etc.

        for ufemb in f[sipm].keys():

            time_list = []
            res2_list = []
            hour_list = []

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

                # ----------------------------
                # Gain2
                # ----------------------------
                gain2 = fitted_centers[2] - fitted_centers[1]
                if gain2 < 100:
                    continue

                # ----------------------------
                # Resolution2
                # ----------------------------
                res2 = fwhms[1] * 100.0 / gain2
                if np.isnan(res2) or res2 <= 0:
                    continue

                time_list.append(dt)
                hour_list.append(dt.hour)
                res2_list.append(res2)

            if not time_list:
                continue

            # ----------------------------
            # Sort chronologically
            # ----------------------------
            time_list, hour_list, res2_list = zip(
                *sorted(zip(time_list, hour_list, res2_list))
            )

            hours_since_start = np.array([
                (t - time_list[0]).total_seconds() / 3600.0
                for t in time_list
            ])

            res2_arr = np.array(res2_list)

            # --------------------------------------------------
            # ✅ ACTUAL WORKING FILTER
            #   HV1 channel 05 & 15 only
            #   Remove any resolution > 10
            # --------------------------------------------------
            if hv_prefix == "HV1" and chan in ["05", "15"]:
                mask = res2_arr > 10
                print(f"{sipm}: removing {np.sum(mask)} points > 10")
                res2_arr = np.where(mask, np.nan, res2_arr)

            # ----------------------------
            # Normalize AFTER cleaning
            # ----------------------------
            res2_norm = res2_arr / np.nanmean(res2_arr)

            hv_groups[hv_prefix][sipm] = {
                "hours": hours_since_start,
                "hours_of_day": np.array(hour_list),
                "res2_raw": res2_arr,
                "res2_norm": res2_norm,
            }

# ----------------------------
# Plotting helper
# ----------------------------
def plot_subplots(hv, channels, ykey, ylabel, ylim, filename):

    n_channels = len(channels)
    ncols = 6
    nrows = int(np.ceil(n_channels / ncols))

    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(20, 10),
        sharex=True,
        sharey=False,
    )

    axes = axes.flatten()

    for i, (sipm, data) in enumerate(channels.items()):
        ax = axes[i]

        for hr in target_hours:
            idx = np.where(data["hours_of_day"] == hr)[0]
            ax.plot(
                data["hours"][idx],
                data[ykey][idx],
                "+-",
                markersize=3,
                color=colors[hr],
                label=f"{labels[hr]}" if i == 0 else "",
            )

        ax.set_title(sipm, fontsize=9)
        ax.grid(True, ls="--", alpha=0.5)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(0.1))

        if ylim is not None:
            ax.set_ylim(*ylim)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(f"{ylabel} per Channel - {hv}", fontsize=14)
    fig.text(0.5, 0.05, "Hours", ha="center")
    fig.text(0.06, 0.5, ylabel, va="center", rotation="vertical")

    plt.subplots_adjust(
        left=0.1,
        right=0.98,
        top=0.9,
        bottom=0.1,
        wspace=0.3,
        hspace=0.4,
    )

    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {save_path}")

# ----------------------------
# Plot per HV group
# ----------------------------
for hv, channels in hv_groups.items():

    if not channels:
        continue

    plot_subplots(
        hv=hv,
        channels=channels,
        ykey="res2_norm",
        ylabel="Normalized Resolution",
        ylim=(0.75, 1.25),
        filename=f"{hv}_Normalized_Res2_subplots.png",
    )

    plot_subplots(
        hv=hv,
        channels=channels,
        ykey="res2_raw",
        ylabel="Resolution (%)",
        ylim=None,
        filename=f"{hv}_Raw_Res2_subplots.png",
    )
