#!/usr/bin/env python3

import numpy as np
import sys
import os
import time
from datetime import datetime, timezone
import pytz
import struct
import codecs
import pickle
from shutil import copyfile
import shutil
import h5py
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd
import argparse
from collections import defaultdict

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# ----------------------------
# CLI Argument Parser
# ----------------------------

parser = argparse.ArgumentParser()
parser.add_argument(
    "--prefix",
    default="HV3",
    help="Device prefix to analyze (e.g. HV1, HV2)"
)
args, unknown = parser.parse_known_args()

desired_prefix = args.prefix
print(f"Processing only channels starting with: {desired_prefix}")

# ----------------------------
# Gaussian function
# ----------------------------

def gaussian(x, A, mu, sigma):
    return A * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))

# ----------------------------
# Map setup
# ----------------------------

fm = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/CE_LD/chn_mapping.csv"
dmap = {}
if os.path.isfile(fm):
    with open(fm, "r") as f:
        for line in f:
            if "femb" in line:
                continue
            else:
                tmps = line.strip().split(",")
                chno = int(tmps[6])
                if len(tmps[12]) >= 0:
                    sipmno = tmps[12][0:3] + "_" + tmps[9] + "_" + tmps[11] + "_" + "CH%02d" % chno + "_FNL" + tmps[4]
                    dmap[chno] = sipmno
else:
    print(f"{fm} doesn't exist")
    exit()

# ----------------------------
# HDF5 utilities
# ----------------------------

def create_grp_hdf5(hdf5_fp):
    if not os.path.exists(hdf5_fp):
        with h5py.File(hdf5_fp, 'w') as f:
            for onekey in dmap.keys():
                sipmno = dmap[onekey]
                if 'OPEN' not in sipmno:
                    f.create_group(sipmno)
            dt = h5py.string_dtype(encoding='utf-8')
            f.create_dataset("file_analyzed", shape=(0,), maxshape=(None,), dtype=dt, chunks=True)
        print("File and groups created.")

def append_data(hdf5_fp, sipmno, dsetn, dsetd, attrsd):
    with h5py.File(hdf5_fp, 'a') as f:
        subgrp = f['/' + sipmno]
        ds = subgrp.get(dsetn, default=None)
        if ds is None:
            subgrp.create_dataset(dsetn, data=dsetd, dtype=np.dtype([("PeakADC", "f4"), ("PeakCNT", "f4")]))
            ds = subgrp[dsetn]
            for onekey in attrsd.keys():
                ds.attrs[onekey] = attrsd[onekey]

def append_anaed_fp(hdf5_fp, anafp):
    with h5py.File(hdf5_fp, 'a') as f:
        dset = f["file_analyzed"]
        old_size = dset.shape[0]
        dset.resize((old_size + 1,))
        dset[old_size:] = anafp

def filter_anaed_file(hdf5_fp, anafp):
    with h5py.File(hdf5_fp, 'r') as f:
        dset = f["file_analyzed"]
        fns = dset[:]
        for fn in fns:
            if (anafp in str(fn)) and ("20250530" in str(fn)):
                return True
        return False

# ----------------------------
# Main Analysis
# ----------------------------

rootdir = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/"

# Data structures for storing plots
daily_gain_data = defaultdict(lambda: defaultdict(list))
daily_res_data = defaultdict(lambda: defaultdict(list))
daily_snr_data = defaultdict(lambda: defaultdict(list))

# Track channel statuses for reporting
channel_status = dict()

for subdir in [d for d in os.listdir(rootdir) if d.startswith("Result_")]:
    rst_dir = os.path.join(rootdir, subdir)
    print(rst_dir)

    for ufemb_id in [1, 2]:
        hdf5_fp = os.path.join(rst_dir, f"uFEMB{ufemb_id}_{subdir[7:15]}_trigger.hdf5")

        if not os.path.isfile(hdf5_fp):
            print(f"File not found: {hdf5_fp}")
            continue

        with h5py.File(hdf5_fp, "r") as f:
            fns = f.get("file_analyzed", [])
            if len(fns) == 0:
                print(f"No analyzed files found in {hdf5_fp}")
                continue

            fns = sorted([fn.decode('utf-8') for fn in fns])
            fn0 = fns[0]
            ts0 = int(fn0[fn0.find(".tana") - 32:fn0.find(".tana")])
            dt0 = datetime.strptime(fn0[7:7+14], "%Y%m%d_%H_%M").replace(tzinfo=ZoneInfo("America/New_York"))
            dtt0 = int(dt0.timestamp())

            for ch in range(32):
                key = f"CH{ch:02d}"
                ch_global = (ufemb_id - 1) * 32 + ch

                if ch_global not in dmap:
                    channel_status[ch_global] = f"No mapping found for global channel {ch_global}"
                    continue

                dn = dmap[ch_global]
                if "OPEN" in dn:
                    channel_status[ch_global] = f"Channel {dn} ignored (OPEN)"
                    continue

                if not dn.startswith(desired_prefix):
                    channel_status[ch_global] = f"Channel {dn} skipped (prefix mismatch)"
                    continue

                data = f.get(key, None)
                if data is None or len(data) == 0:
                    channel_status[ch_global] = f"Channel {dn} has no data"
                    continue

                ts, ds = zip(*data)
                ts = np.array(ts) - ts0 * 10
                ds = np.array(ds)

                diffs = ts[1:] - ts[:-1]
                jumps = np.where(diffs > 1e9)[0]

                subts, subds = [], []
                prev = 0
                for idx in jumps:
                    subt = ts[prev:idx+1]
                    subd = ds[prev:idx+1]
                    if len(subd[subd > 30]) < 10:
                        prev = idx+1
                        continue
                    subts.append(subt)
                    subds.append(subd)
                    prev = idx+1

                subts.append(ts[prev:])
                subds.append(ds[prev:])

                processed_any = False

                for xi in range(len(subts)):
                    if len(subds[xi]) < 20:
                        continue

                    dtt00 = dtt0 + int(subts[xi][0] // 1e9)
                    dt = datetime.fromtimestamp(dtt00, tz=pytz.timezone("America/New_York"))

                    if dt.hour in [0, 8, 21]:
                        vbinw = 1
                        counts, bin_edges = np.histogram(subds[xi],
                            bins=range(int(min(subds[xi])), int(max(subds[xi])) + vbinw, vbinw))
                        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
                        peaks, properties = find_peaks(counts, prominence=20, distance=30)

                        fitted_centers = []
                        fitted_sigmas = []
                        fitted_amplitudes = []
                        gauss_params = []

                        for peak_idx in peaks[:8]:
                            center = bin_centers[peak_idx]
                            window = (bin_centers > center - 50) & (bin_centers < center + 50)
                            x_fit = bin_centers[window]
                            y_fit = counts[window]
                            if len(x_fit) < 5:
                                continue
                            try:
                                sigma_guess = (x_fit[-1] - x_fit[0]) / 6
                                p0 = [np.max(y_fit), center, sigma_guess]
                                popt, _ = curve_fit(gaussian, x_fit, y_fit, p0=p0)
                                fitted_amplitudes.append(popt[0])
                                fitted_centers.append(popt[1])
                                fitted_sigmas.append(popt[2])
                                gauss_params.append(popt)
                            except:
                                continue

                        if len(fitted_centers) < 2 or len(fitted_sigmas) < 1:
                            continue

                        fwhm_p0 = 2 * np.sqrt(2 * np.log(2)) * fitted_sigmas[0]

                        gains = []
                        resolutions = []
                        for i in range(min(7, len(fitted_centers)-1)):
                            delta = fitted_centers[i+1] - fitted_centers[i]
                            gains.append(delta)
                            if fwhm_p0 > 0:
                                res = delta / fwhm_p0
                                resolutions.append(res)

                        snr = np.nan
                        if len(fitted_amplitudes) > 1 and fitted_sigmas[0] > 0:
                            snr = fitted_amplitudes[1] / fitted_sigmas[0]

                        time_hour = dt.hour + dt.minute / 60 + dt.second / 3600
                        date_str = dt.strftime("%Y-%m-%d")

                        for gain_idx, g in enumerate(gains):
                            daily_gain_data[ch_global][date_str].append((time_hour, g, gain_idx))
                        for r in resolutions:
                            daily_res_data[ch_global][date_str].append((time_hour, r))
                        daily_snr_data[ch_global][date_str].append((time_hour, snr))

                        processed_any = True

                if processed_any:
                    channel_status[ch_global] = f"Channel {dn} processed successfully"
                else:
                    channel_status[ch_global] = f"Channel {dn} no valid segments at hours 0,8,21"

# ---------------------------------------------------
# Compute reference averages for normalization
# ---------------------------------------------------

reference_gain = defaultdict(dict)
reference_res = defaultdict(float)

all_channels = sorted(daily_gain_data.keys())

for ch in all_channels:
    dates = sorted(daily_gain_data[ch].keys())
    if not dates:
        continue
    first_date = dates[0]

    gains_on_first_day = np.array(daily_gain_data[ch][first_date])
    for gain_idx in range(3):
        mask = gains_on_first_day[:, 2] == gain_idx
        if np.any(mask):
            avg = np.mean(gains_on_first_day[mask, 1])
            reference_gain[ch][gain_idx] = avg

    res_vals = daily_res_data[ch].get(first_date, [])
    if res_vals:
        _, res = zip(*res_vals)
        reference_res[ch] = np.mean(res)

# ---------------------------------------------------
# Plot all daily figures
# ---------------------------------------------------

res_colors = ['purple', 'magenta', 'brown']

dates_to_plot = sorted(set(date for d in daily_gain_data.values() for date in d))

# Pick only first 18 channels for plotting
channels_to_plot = all_channels[:18]

for date in dates_to_plot:
    n_channels = len(channels_to_plot)
    n_rows = 3
    n_cols = 6

    fig_gain, axs_gain = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 3), sharex=True)
    fig_res, axs_res = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 3), sharex=True)
    fig_norm_gain, axs_norm_gain = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 3), sharex=True)
    fig_norm_res, axs_norm_res = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 3), sharex=True)
    fig_snr, axs_snr = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 3), sharex=True)

    fig_gain.suptitle(f"Gain vs Time on {date}")
    fig_norm_gain.suptitle(f"Normalized Gain vs Time on {date}")
    fig_res.suptitle(f"Resolution vs Time on {date}")
    fig_norm_res.suptitle(f"Normalized Resolution vs Time on {date}")
    fig_snr.suptitle(f"SNR vs Time on {date}")

    gain_styles = [
        {'marker': '^', 'color': 'blue',  'label': 'Gain 1'},
        {'marker': '^', 'color': 'green', 'label': 'Gain 2'},
        {'marker': '^', 'color': 'red',   'label': 'Gain 3'},
    ]

    for i in range(n_rows * n_cols):
        row, col = divmod(i, n_cols)

        # If fewer than 18 channels, hide excess axes
        if i >= n_channels:
            axs_gain[row, col].axis('off')
            axs_norm_gain[row, col].axis('off')
            axs_res[row, col].axis('off')
            axs_norm_res[row, col].axis('off')
            axs_snr[row, col].axis('off')
            continue

        ch = channels_to_plot[i]

        ax_g = axs_gain[row, col]
        ax_ng = axs_norm_gain[row, col]
        ax_r = axs_res[row, col]
        ax_nr = axs_norm_res[row, col]
        ax_s = axs_snr[row, col]

        gain_vals = daily_gain_data[ch].get(date, [])
        res_vals = daily_res_data[ch].get(date, [])
        snr_vals = daily_snr_data[ch].get(date, [])

        if gain_vals:
            gain_vals = np.array(gain_vals)
            for gain_idx in range(3):
                mask = gain_vals[:, 2] == gain_idx
                if np.any(mask):
                    hours = gain_vals[mask, 0]
                    gains = gain_vals[mask, 1]
                    ref = reference_gain[ch].get(gain_idx, 1.0)
                    norm_gains = gains / ref

                    style = gain_styles[gain_idx]
                    label = style['label'] if i == 0 else None
                    ax_g.scatter(hours, gains, marker=style['marker'], color=style['color'], label=label, s=40)
                    ax_ng.scatter(hours, norm_gains, marker=style['marker'], color=style['color'], label=label, s=40)

            ax_g.set_title(f"CH{ch:02d}")
            ax_ng.set_title(f"CH{ch:02d}")
            ax_g.set_ylabel("Gain")
            ax_ng.set_ylabel("Normalized Gain")
            ax_g.grid()
            ax_ng.grid()
            if i == 0:
                ax_g.legend(fontsize='small')
                ax_ng.legend(fontsize='small')

        if res_vals:
            res_vals = np.array(res_vals)
            hours = res_vals[:, 0]
            res = res_vals[:, 1]
            ref_res = reference_res.get(ch, 1.0)
            norm_res = res / ref_res

            for idx, color in enumerate(res_colors):
                if idx >= len(res):
                    break
                ax_r.scatter(hours[idx], res[idx], marker='+', color=color, s=50,
                             label=f'Res {idx+1}' if i == 0 else None)
            if len(res) > 3:
                ax_r.scatter(hours[3:], res[3:], marker='+', color='gray', s=50)

            for idx, color in enumerate(res_colors):
                if idx >= len(norm_res):
                    break
                ax_nr.scatter(hours[idx], norm_res[idx], marker='+', color=color, s=50,
                              label=f'Norm Res {idx+1}' if i == 0 else None)
            if len(norm_res) > 3:
                ax_nr.scatter(hours[3:], norm_res[3:], marker='+', color='gray', s=50)

            ax_r.set_title(f"CH{ch:02d}")
            ax_nr.set_title(f"CH{ch:02d}")
            ax_r.set_ylabel("Resolution")
            ax_nr.set_ylabel("Normalized Resolution")
            ax_r.grid()
            ax_nr.grid()

            if i == 0:
                ax_r.legend(fontsize='small')
                ax_nr.legend(fontsize='small')

        if snr_vals:
            snr_vals = np.array(snr_vals)
            hours = snr_vals[:, 0]
            snr = snr_vals[:, 1]
            ax_s.scatter(hours, snr, color='orange', s=40)
            ax_s.set_title(f"CH{ch:02d}")
            ax_s.set_ylabel("SNR")
            ax_s.grid()

    fig_gain.tight_layout()
    fig_norm_gain.tight_layout()
    fig_res.tight_layout()
    fig_norm_res.tight_layout()
    fig_snr.tight_layout()

    # Optional saving:
    fig_gain.savefig(f"gain_{date}.png")
    fig_norm_gain.savefig(f"norm_gain_{date}.png")
    fig_res.savefig(f"res_{date}.png")
    fig_norm_res.savefig(f"norm_res_{date}.png")
    fig_snr.savefig(f"snr_{date}.png")

plt.show()
