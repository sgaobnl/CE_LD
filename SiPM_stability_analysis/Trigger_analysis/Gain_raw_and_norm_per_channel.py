import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime

# ----------------------------
# Paths
# ----------------------------
rootdir = "/data/disk1/koloina/waveform_fitting/SIPM/Final_plots/"
hdf5_path = os.path.join(rootdir, "LED_Analysis_Final.hdf5")

norm_output_dir = os.path.join(rootdir, "Norm_gain")
raw_output_dir  = os.path.join(rootdir, "Raw_gain")

os.makedirs(norm_output_dir, exist_ok=True)
os.makedirs(raw_output_dir, exist_ok=True)

# ----------------------------
# Plot settings
# ----------------------------
target_hours = [0, 8, 21]

colors = {0: "#084594", 8: "purple", 21: "black"}
labels = {0: "00h", 8: "08h", 21: "21h"}

# Y-limits for RAW Gain
raw_ylim = {
    "HV1": (0, 200),
    "HV2": (0, 300),
    "HV3": (0, 350),
}

# ----------------------------
# Collect data per HV
# ----------------------------
hv_groups = {"HV1": {}, "HV2": {}, "HV3": {}}

with h5py.File(hdf5_path, "r") as f:
    for sipm in f.keys():

        hv_prefix = next((hv for hv in hv_groups if hv in sipm), None)
        if hv_prefix is None:
            continue

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

                # ----------------------------
                # Raw Gain2
                # ----------------------------
                gain2 = fitted_centers[2] - fitted_centers[1]

                if gain2 < 115:
                    gain2 = np.nan

                time_list.append(dt)
                hour_list.append(dt.hour)
                gain2_list.append(gain2)

            if len(time_list) == 0:
                continue

            # ----------------------------
            # Sort & convert times
            # ----------------------------
            time_list, hour_list, gain2_list = zip(
                *sorted(zip(time_list, hour_list, gain2_list))
            )

            hours_since_start = [
                (t - time_list[0]).total_seconds() / 3600.0
                for t in time_list
            ]

            gain2_list = np.array(gain2_list)

            # ----------------------------
            # Normalization
            # ----------------------------
            valid = gain2_list[~np.isnan(gain2_list)]
            if len(valid) == 0:
                continue

            mean_gain = np.mean(valid)
            norm_gain2 = gain2_list / mean_gain

            hv_groups[hv_prefix][sipm] = {
                "hours": np.array(hours_since_start),
                "hours_of_day": np.array(hour_list),
                "gain2": gain2_list,
                "norm_gain2": norm_gain2,
            }

# ============================================================
# Plotting function
# ============================================================
def make_subplot_page(hv, channels, ydata_key, ylim, ylabel, outfile):

    n_channels = len(channels)
    ncols = 6
    nrows = int(np.ceil(n_channels / ncols))

    fig, axes = plt.subplots(
        nrows, ncols, figsize=(20, 10),
        sharex=True, sharey=True
    )
    axes = axes.flatten()

    for i, (sipm, data) in enumerate(channels.items()):
        ax = axes[i]

        for hr in target_hours:
            idx = np.where(data["hours_of_day"] == hr)[0]
            ax.plot(
                data["hours"][idx],
                data[ydata_key][idx],
                "+-",
                color=colors[hr],
                markersize=3,
                label=labels[hr] if i == 0 else ""
            )

        ax.set_title(sipm, fontsize=9)
        ax.grid(True, ls="--", alpha=0.5)
        ax.set_ylim(*ylim)

    # Remove unused subplots
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    fig.suptitle(outfile.replace(".png", ""), fontsize=14)
    fig.text(0.5, 0.04, "Hours since start", ha="center")
    fig.text(0.1, 0.5, ylabel, va="center", rotation="vertical")

    plt.savefig(outfile, bbox_inches="tight")
    plt.close(fig)

    print(f"Saved: {outfile}")

# ============================================================
# Create plots
# ============================================================
for hv, channels in hv_groups.items():
    if len(channels) == 0:
        continue

    # ----------------------------
    # Normalized Gain2 plots
    # ----------------------------
    norm_file = os.path.join(
        norm_output_dir,
        f"{hv}_normalized_gain2_subplots.png",
    )

    make_subplot_page(
        hv=hv,
        channels=channels,
        ydata_key="norm_gain2",
        ylim=(0.95, 1.05),
        ylabel="Normalized Gain2",
        outfile=norm_file,
    )

    # ----------------------------
    # Raw Gain2 plots
    # ----------------------------
    raw_file = os.path.join(
        raw_output_dir,
        f"{hv}_raw_gain2_subplots.png",
    )

    make_subplot_page(
        hv=hv,
        channels=channels,
        ydata_key="gain2",
        ylim=raw_ylim[hv],
        ylabel="Raw Gain2",
        outfile=raw_file,
    )
