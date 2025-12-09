#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plot PDE vs time (both NORMALIZED and NON-NORMALIZED) for all channels from
combined_pde_by_hour.hdf5

For each HV group (HV1, HV2, HV3):
  - Two figures: one normalized, one non-normalized
  - 18 subplots (1 per channel)
  - X-axis: hours since first timestamp
  - Negative PDE values excluded
  - Generate ASCII files for each channel
  
FILTERS:
  - HV1: Exclude first 572 hours from plots and mean calculation
  - HV2/HV3: Exclude PDE > 5 from plots and mean calculation
"""

import os
import re
import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# --------------------------------------------------
# PATHS
# --------------------------------------------------

input_hdf5 = "/data/disk1/koloina/CN/combined_pde_by_hour.hdf5"
output_dir = "/data/disk1/koloina/CN/PDE_NORM_PLOTS"
ascii_dir = os.path.join(output_dir, "ASCII_FILES")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(ascii_dir, exist_ok=True)

# --------------------------------------------------
# TIMESTAMP PARSER
# --------------------------------------------------

def parse_trigger_ts(ts):
    """Parse trigger timestamp: YYYY-MM-DD HH:MM:SS"""
    try:
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    except:
        return None


# --------------------------------------------------
# CHANNEL → HV
# --------------------------------------------------

def get_hv_from_channel(channel_name):
    """
    Extract HV group from channel label
    Example: HV1_P1_A1_CH01_FNL1425 -> HV1
    """
    m = re.search(r"(HV\d+)", channel_name)
    return m.group(1) if m else "UNKNOWN"


def get_channel_number(channel_name):
    """
    Extract channel number for sorting
    Example: HV1_P1_A1_CH01_FNL1425 -> 1
    """
    m = re.search(r"CH(\d+)", channel_name)
    return int(m.group(1)) if m else 999


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def load_data():

    """
    Returns:
        data_normalized[HV][channel] = list of (hour_since_start, norm_pde)
        data_raw[HV][channel] = list of (hour_since_start, pde)
    """

    raw = {}
    all_times = []

    # ---------------- Collect timestamps ----------------

    with h5py.File(input_hdf5, "r") as f:
        for channel in f:
            for ufemb in f[channel]:
                for ts in f[channel][ufemb]:
                    dt = parse_trigger_ts(ts)
                    if dt:
                        all_times.append(dt)

    if not all_times:
        raise RuntimeError("No timestamps found!")

    t0 = min(all_times)
    print(f"\nGlobal t0 = {t0}")

    # ---------------- Read PDE ----------------

    with h5py.File(input_hdf5, "r") as f:

        for channel in f:

            hv = get_hv_from_channel(channel)
            raw.setdefault(hv, {})
            raw[hv].setdefault(channel, [])

            for ufemb in f[channel]:

                for ts in f[channel][ufemb]:

                    dt = parse_trigger_ts(ts)
                    if dt is None:
                        continue

                    hours = (dt - t0).total_seconds() / 3600.0

                    grp = f[channel][ufemb][ts]

                    if "pde_sum" not in grp:
                        continue

                    pde = grp["pde_sum"][()]

                    if np.isnan(pde) or pde <= 0:
                        continue

                    raw[hv][channel].append((hours, pde))

    # ---------------- Apply filters and create both normalized and raw datasets ----------------

    data_normalized = {}
    data_raw = {}

    for hv, channels in raw.items():

        data_normalized[hv] = {}
        data_raw[hv] = {}

        for ch, points in channels.items():

            if len(points) == 0:
                continue

            # Apply HV-specific filters
            filtered_points = []
            for t, v in points:
                # HV1: exclude first 572 hours
                if hv == "HV1" and t < 572:
                    continue
                # HV2/HV3: exclude PDE > 5
                if hv in ["HV2", "HV3"] and v > 3:
                    continue
                filtered_points.append((t, v))

            if len(filtered_points) == 0:
                continue

            # Sort by time
            filtered_points.sort(key=lambda x: x[0])

            # Store raw (non-normalized) data
            data_raw[hv][ch] = filtered_points

            # Calculate mean for normalization
            pdes = np.array([p[1] for p in filtered_points])
            mean_pde = np.mean(pdes)

            # Skip channels with invalid means
            if mean_pde <= 0:
                continue

            # Store normalized data
            normalized = [
                (t, v / mean_pde)
                for t, v in filtered_points
            ]

            data_normalized[hv][ch] = normalized

    return data_normalized, data_raw


# --------------------------------------------------
# ASCII OUTPUT
# --------------------------------------------------

def write_ascii_files(data_normalized, data_raw):
    """
    Write ASCII files for each channel with both raw and normalized PDE values
    """
    
    print("\nWriting ASCII files...")
    
    for hv in data_raw.keys():
        
        # Get all channels for this HV group
        channels = set(data_raw[hv].keys()) | set(data_normalized[hv].keys())
        
        for ch in channels:
            
            # Get data for this channel
            raw_points = data_raw[hv].get(ch, [])
            norm_points = data_normalized[hv].get(ch, [])
            
            if not raw_points and not norm_points:
                continue
            
            # Create filename (sanitize channel name)
            safe_ch_name = ch.replace("/", "_").replace(" ", "_")
            ascii_file = os.path.join(ascii_dir, f"{safe_ch_name}.txt")
            
            with open(ascii_file, "w") as f:
                # Write header
                f.write(f"# Channel: {ch}\n")
                f.write(f"# HV Group: {hv}\n")
                f.write(f"# Columns: Hours_Since_Start  PDE_Raw  PDE_Normalized\n")
                f.write("#" + "-" * 60 + "\n")
                
                # Combine data (use raw data as reference since it should have all points)
                for i, (t, raw_pde) in enumerate(raw_points):
                    # Find corresponding normalized value
                    norm_pde = "N/A"
                    if i < len(norm_points) and abs(norm_points[i][0] - t) < 0.01:
                        norm_pde = f"{norm_points[i][1]:.6f}"
                    
                    f.write(f"{t:12.4f}  {raw_pde:12.6f}  {norm_pde:>12s}\n")
            
            print(f"  Written: {ascii_file}")


# --------------------------------------------------
# PLOTTING
# --------------------------------------------------

def plot_by_hv(data, plot_type="normalized"):

    """
    plot_type: "normalized" or "raw"
    """

    for hv, channels in data.items():

        # Sort channels by channel number
        ch_list = sorted(channels.keys(), key=get_channel_number)
        n_channels = len(ch_list)

        if n_channels == 0:
            print(f"Skipping {hv}: no valid channels")
            continue

        print(f"\nPlotting {plot_type} PDE for {hv} ({n_channels} channels)")

        ncols = 6
        nrows = int(np.ceil(n_channels / ncols))

        fig, axs = plt.subplots(
            nrows,
            ncols,
            figsize=(15, 3 * nrows),
            sharex=True,
            sharey=True,
        )

        axs = np.array(axs).reshape(-1)

        for i, ch in enumerate(ch_list):

            ax = axs[i]
            points = channels[ch]

            if not points:
                ax.set_title(ch)
                ax.text(0.5, 0.5, "No Data", ha="center", va="center")
                continue

            x = np.array([p[0] for p in points])
            y = np.array([p[1] for p in points])

            ax.plot(x, y, marker="o", linestyle="-", markersize=2)

            # Add vertical green line at 572 hours for HV1
            if hv == "HV1":
                ax.axvline(x=572, color='green', linestyle='--', linewidth=1.5, alpha=0.7)
                # Add text label below the line
                ax.text(572, ax.get_ylim()[0], '572', 
                       color='green', fontsize=7, ha='center', va='bottom')

            ax.set_title(ch, fontsize=8)
            
            if plot_type == "normalized":
                ax.set_ylim(0.5, 1.5)
            # For raw data, let matplotlib autoscale
            
            ax.grid(True)

        # Hide unused panels
        for j in range(i + 1, len(axs)):
            axs[j].axis("off")

        if plot_type == "normalized":
            fig.suptitle(
                f"Normalized PDE vs Time for {hv} Channels",
                fontsize=16
            )
            fig.supylabel("Normalized PDE")
        else:
            fig.suptitle(
                f"PDE vs Time for {hv} Channels",
                fontsize=16
            )
            fig.supylabel("PDE")

        fig.supxlabel("Hours")

        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if plot_type == "normalized":
            out_file = os.path.join(output_dir, f"PDE_{hv}_18channels_NORMALIZED.png")
        else:
            out_file = os.path.join(output_dir, f"PDE_{hv}_18channels_RAW.png")
            
        plt.savefig(out_file, dpi=200)
        plt.close()

        print(f"  Saved -> {out_file}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\nLoading PDE data...")
    print("  Filter: HV1 excludes first 572 hours")
    print("  Filter: HV2/HV3 exclude PDE > 3")

    data_normalized, data_raw = load_data()

    print("\nProducing normalized PDE plots...")
    plot_by_hv(data_normalized, plot_type="normalized")

    print("\nProducing raw (non-normalized) PDE plots...")
    plot_by_hv(data_raw, plot_type="raw")

    write_ascii_files(data_normalized, data_raw)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
