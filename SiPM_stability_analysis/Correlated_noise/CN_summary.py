# -*- coding: utf-8 -*-
"""
Compute CN mean & std per channel (SiPM), grouped by HV1/HV2/HV3,
plot mean CN with error bars showing ±1σ std deviation,
and save all channel statistics to a text file.
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# Paths
# ============================================================
HDF5_FILE = "/data/disk1/koloina/CN/SiPM/New_Corr_noise_improved_final.hdf5"
OUTPUT_TXT = "/data/disk1/koloina/CN/SiPM/CN_channel_statistics.txt"

# ============================================================
# Helper: identify HV from SiPM group name
# ============================================================
def get_hv_group(sipm_name):
    prefix = sipm_name.split("_")[0]
    return prefix if prefix in ["HV1", "HV2", "HV3"] else None

# ============================================================
# Read CN values per channel
# ============================================================
channel_names = []
hv_groups = []
channel_means = []
channel_stds = []

with h5py.File(HDF5_FILE, "r") as f:
    for sipm_name in f.keys():
        if sipm_name == "file_analyzed":
            continue
        hv = get_hv_group(sipm_name)
        if hv is None:
            continue

        cn_list = []
        for dset_name in f[sipm_name].keys():
            dset = f[f"{sipm_name}/{dset_name}"]
            if "CN" in dset.dtype.fields:
                cn = dset["CN"][0]
                if np.isfinite(cn) and cn >= 0:
                    cn_list.append(cn)

        if len(cn_list) == 0:
            continue

        arr = np.array(cn_list)
        channel_names.append(sipm_name)
        hv_groups.append(hv)
        channel_means.append(np.mean(arr))
        channel_stds.append(np.std(arr))

# Convert to numpy arrays
channel_means = np.array(channel_means)
channel_stds = np.array(channel_stds)
hv_groups = np.array(hv_groups)

# ============================================================
# Save channel statistics to a text file
# ============================================================
with open(OUTPUT_TXT, "w") as ftxt:
    ftxt.write("Channel_Name\tHV_Group\tCN_Mean\tCN_Std\n")
    for name, hv, mean_val, std_val in zip(channel_names, hv_groups, channel_means, channel_stds):
        ftxt.write(f"{name}\t{hv}\t{mean_val:.6f}\t{std_val:.6f}\n")

print(f"Channel statistics saved to: {OUTPUT_TXT}")

# ============================================================
# PLOT: CN mean ± std error bars per channel
# ============================================================
plt.figure(figsize=(20, 8))
x = np.arange(len(channel_means))
colors = {"HV1": "blue", "HV2": "green", "HV3": "red"}

for hv in ["HV1", "HV2", "HV3"]:
    idx = np.where(hv_groups == hv)[0]

    plt.errorbar(
        x[idx],
        channel_means[idx],
        yerr=channel_stds[idx],
        fmt='o',
        capsize=4,
        markersize=6,
        color=colors[hv],
        alpha=0.9,
        label=None  # no legend on plot
    )

# Annotate std value above each error bar
for xi, mean_val, std_val in zip(x, channel_means, channel_stds):
    plt.text(
        xi, mean_val + std_val + 0.005,
        f"{std_val:.3f}",
        ha='center',
        va='bottom',
        fontsize=8,
        rotation=90
    )

# Full channel names on x-axis
plt.xticks(x, channel_names, rotation=90, fontsize=8)
plt.xlabel("Channel")
plt.ylabel("CN Mean ± 1σ")
plt.title("CN Mean with Standard Deviation per Channel (Full Experiment)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
