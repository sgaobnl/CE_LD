# -*- coding: utf-8 -*-
"""
Plot normalized CN (CN / mean(CN)) vs hours for each HV group.
1 figure per HV group, 18 subplots each.
Saves the plots under a new folder.
For HV1, filter hours < 572 and show a vertical line at 572h.
"""

import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ----------------------------
# Paths
# ----------------------------
rootdir = "/data/disk1/koloina/CN/SiPM/"
hdf5_fp = os.path.join(rootdir, "New_Corr_noise_improved_final.hdf5")
output_dir = os.path.join(rootdir, "new_cn_normplots")
os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Load data grouped by HV
# ----------------------------
hv_groups = {}

with h5py.File(hdf5_fp, "r") as f:
    for sipm_name in f.keys():
        if sipm_name == "file_analyzed":
            continue

        hv_prefix = sipm_name.split("_")[0]
        hv_groups.setdefault(hv_prefix, {})

        entries = []
        for dset_name in f[sipm_name].keys():
            dset = f[sipm_name][dset_name]
            cn_val = dset["CN"][()]
            try:
                dt = datetime.strptime(dset_name, "%Y_%m_%d_%H")
                entries.append((dt, cn_val))
            except Exception:
                continue

        entries.sort(key=lambda x: x[0])
        hv_groups[hv_prefix][sipm_name] = entries

# ----------------------------
# Plot normalized CN per HV group
# ----------------------------
for hv, ch_dict in hv_groups.items():
    if len(ch_dict) == 0:
        continue

    fig, axes = plt.subplots(3, 6, figsize=(20, 10), sharex=True)
    axes = axes.flatten()

    # compute reference time
    all_times = [t for ch_data in ch_dict.values() for t, _ in ch_data]
    if not all_times:
        continue
    t0 = min(all_times)

    for i, (sipm_name, data) in enumerate(sorted(ch_dict.items())[:18]):
        if len(data) == 0:
            continue

        # compute hours
        hours = np.array([(t - t0).total_seconds() / 3600 for t, _ in data])
        CN_vals = np.array([cn for _, cn in data], dtype=float)

        # HV1: keep hours >= 572
        if hv == "HV1":
            mask = hours >= 572
            hours = hours[mask]
            CN_vals = CN_vals[mask]

        if len(CN_vals) == 0:
            continue

        # normalize
        mean_cn = np.mean(CN_vals[CN_vals > 0]) if np.any(CN_vals > 0) else 1
        CN_norm = CN_vals / mean_cn

        ax = axes[i]
        ax.axhline(1, color='red', linestyle='--', linewidth=1)
        ax.plot(hours, CN_norm, marker='o', markersize=2, lw=0.8)
        ax.set_title(sipm_name, fontsize=8)
        ax.grid(True, ls='--', alpha=0.3)
        ax.set_ylim(0.5, 1.5)

        # ----------------------------
        # Add vertical line for HV1 filtering start
        # ----------------------------
        if hv == "HV1":
            ax.axvline(572, color='red', linestyle=':', linewidth=1)

    # remove unused subplots
    for j in range(len(ch_dict), 18):
        fig.delaxes(axes[j])

    fig.suptitle(f"{hv} – Normalized CN vs Hours", fontsize=14)
    fig.text(0.5, 0.04, "Hours", ha='center')
    fig.text(0.04, 0.5, "Normalized CN", va='center', rotation='vertical')

    plt.tight_layout(rect=[0.04, 0.04, 1, 0.95])

    # ----------------------------
    # Save the figure
    # ----------------------------
    savepath = os.path.join(output_dir, f"{hv}_CN_norm_vs_hours.png")
    plt.savefig(savepath, dpi=200)
    plt.close(fig)
    print(f"Saved {savepath}")
