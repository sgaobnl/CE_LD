#!/usr/bin/env python3
import os
from datetime import datetime
from typing import Dict, List, Optional

import h5py
import matplotlib.pyplot as plt
import numpy as np


# ----------------------------
# Configuration
# ----------------------------
rootdir = "Input path"
hdf5_path = os.path.join(rootdir, "Trig_Analysis.hdf5")
output_dir = os.path.join(rootdir, "PDE_vs_hours_plots")
os.makedirs(output_dir, exist_ok=True)


# ----------------------------
# Robust date parser (covers the formats you actually have)
# ----------------------------
def parse_date(date_str: str) -> Optional[datetime]:
    # The keys in your file look like: 2025-11-06 14:30:22
    # Some may contain microseconds → strip them first
    clean = date_str.split('.')[0]
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(clean, fmt)
        except ValueError:
            continue
    # If everything fails, print a warning (helps debugging)
    print(f"Warning: Could not parse date '{date_str}'")
    return None


# ----------------------------
# 1. Gather raw data
# ----------------------------
hv_groups: Dict[str, Dict[str, Dict[str, List]]] = {"HV1": {}, "HV2": {}, "HV3": {}}

with h5py.File(hdf5_path, "r") as f:
    for sipm_key in f.keys():                     # e.g. HV2_CON1_1_CH03_FNLXYZ
        hv_prefix = sipm_key.split("_")[0]
        if hv_prefix not in hv_groups:
            continue

        grp = f[sipm_key]
        for femb_key in grp.keys():               # uFEMB1 or uFEMB2
            femb_grp = grp[femb_key]
            for date_key in femb_grp.keys():
                dset = femb_grp[date_key]
                if "envelope_mu" not in dset.attrs:
                    continue

                # ---- force float ----
                try:
                    env_mu = float(dset.attrs["envelope_mu"])
                except Exception:
                    continue

                dt = parse_date(date_key)
                if dt is None:
                    continue

                chan = hv_groups[hv_prefix].setdefault(
                    sipm_key, {"dates": [], "mu": []}
                )
                chan["dates"].append(dt)
                chan["mu"].append(env_mu)


# ----------------------------
# 2. Per-HV processing
# ----------------------------
for hv_prefix, channels in hv_groups.items():
    if not channels:
        continue

    # ---- keep only channels that actually have data ----
    channels = {k: v for k, v in channels.items() if len(v["dates"]) > 0}
    if not channels:
        continue

    # ---- mean per channel (over *all* its timestamps) ----
    mean_adc: Dict[str, float] = {}
    for ch, data in channels.items():
        mean_adc[ch] = float(np.mean(data["mu"]))

    # ---- build time-series (per-channel t0, not global) ----
    series: Dict[str, Dict[str, np.ndarray]] = {}
    for ch, data in channels.items():
        dates = np.array(data["dates"])
        mu    = np.array(data["mu"], dtype=float)

        order = np.argsort(dates)
        dates, mu = dates[order], mu[order]

        # **per-channel** reference time
        t0 = dates[0]
        hours = np.array([(d - t0).total_seconds() / 3600.0 for d in dates])

        # Normalise: raw / channel_mean → average = 1.0
        norm = mu / mean_adc[ch]

        series[ch] = {"hours": hours, "norm": norm}

    # ----------------------------
    # 3. Plot
    # ----------------------------
    n_chan = len(series)
    nrows, ncols = 6, 3
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(15, 12), sharex=False, sharey=True
    )
    axes = axes.flatten()

    for idx, (ch_name, s) in enumerate(sorted(series.items())):
        if idx >= len(axes):
            break
        ax = axes[idx]
        ax.plot(s["hours"], s["norm"],
                marker="o", markersize=3, linestyle="-", linewidth=0.8)
        ax.set_title(ch_name, fontsize=8)
        ax.tick_params(axis="x", labelrotation=30, labelsize=7)
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_ylabel("Normalized Envelope ADC", fontsize=8)

    # hide unused sub-plots
    for j in range(idx + 1, len(axes)):
        axes[j].axis("off")

    # x-label on bottom row only
    for ax in axes[-ncols:]:
        ax.set_xlabel("Hours since first measurement", fontsize=8)

    fig.suptitle(
        f"Normalized Envelope ADC vs Hours — {hv_prefix}",
        fontsize=14, fontweight="bold"
    )
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.subplots_adjust(hspace=0.4, wspace=0.3)

    outfile = os.path.join(
        output_dir, f"{hv_prefix}_NormalizedEnvelope_vs_Hours.png"
    )
    plt.savefig(outfile, dpi=300)
    plt.close(fig)
    print(f"Saved: {outfile}")

print("\nAll normalized envelope-vs-hours plots generated.")
