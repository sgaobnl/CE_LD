#----------------------------
Before use, run the code Trigger_data_analysis.py . You should get a .hdf5 file that contains the peaks data (centers, amplitudes, fwhm) , resolution, SNR and PDE.
This code computes normalized gain
#----------------------------
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime

# ----------------------------
# Paths
# ----------------------------
rootdir = "/data/disk1/koloina/waveform_fitting/SIPM/"
hdf5_path = os.path.join(rootdir, "Trig_Analysis.hdf5")
output_dir = os.path.join(rootdir, "test_norm2gain_plots")
os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Plot settings
# ----------------------------
target_hours = [0, 8, 21]
colors = {0: "#084594", 8: "purple", 21: "black"}
labels = {0: "00h", 8: "08h", 21: "21h"}

# ----------------------------
# Collect data per HV
# ----------------------------
hv_groups = {"HV1": {}, "HV2": {}, "HV3": {}}

with h5py.File(hdf5_path, "r") as f:
    for sipm in f.keys():
        hv_prefix = next((hv for hv in hv_groups if hv in sipm), None)
        if hv_prefix is None:
            continue  # skip if not in HV1/2/3

        for ufemb in f[sipm].keys():
            time_list, gain2_list, hour_list = [], [], []

            for date_str in sorted(f[sipm][ufemb].keys()):
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if dt.hour not in target_hours:
                    continue

                dset = f[sipm][ufemb][date_str]
                fitted_centers = np.array(dset["fitted_centers"])
                if len(fitted_centers) < 3:
                    continue

                gain2 = fitted_centers[2] - fitted_centers[1]
                if gain2 < 115:
                    gain2 = np.nan

                time_list.append(dt)
                hour_list.append(dt.hour)
                gain2_list.append(gain2)

            if len(time_list) == 0:
                continue

            # Sort and compute hours since start
            time_list, hour_list, gain2_list = zip(
                *sorted(zip(time_list, hour_list, gain2_list))
            )
            hours_since_start = [(t - time_list[0]).total_seconds() / 3600.0 for t in time_list]

            # Normalization
            valid = [g for g in gain2_list if not np.isnan(g)]
            if len(valid) == 0:
                continue
            mean_gain = np.mean(valid)
            norm_gain2 = np.array(gain2_list) / mean_gain

            hv_groups[hv_prefix][sipm] = {
                "hours": np.array(hours_since_start),
                "hours_of_day": np.array(hour_list),
                "norm_gain2": norm_gain2,
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
            data["norm_gain2"][idx],
            "+-", color=colors[hr],
            markersize=3,  # smaller marker
            label=f"{labels[hr]}" if i == 0 else ""
            )


        ax.set_title(sipm, fontsize=9)
        ax.grid(True, ls="--", alpha=0.5)
        ax.set_ylim(0.95, 1.05)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(0.05))

    # remove unused subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(f"Normalized Gain2 per Channel - {hv}", fontsize=14)
    fig.text(0.5, 0.04, "Hours since start", ha="center")
    fig.text(0.1, 0.5, "Normalized Gain", va="center", rotation="vertical")

    # handles, labels_ = axes[0].get_legend_handles_labels()
    # fig.legend(handles, labels_, loc="upper right", bbox_to_anchor=(1.12, 1.0))
    # plt.tight_layout(rect=[0.04, 0.04, 0.88, 0.95])

    save_path = os.path.join(output_dir, f"{hv}_normalized_gain2_subplots.png")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved normalized Gain2 plot: {save_path}")

