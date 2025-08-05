#!/usr/bin/env python3

import os
import numpy as np
import h5py
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from datetime import datetime
from collections import defaultdict
import pytz

# Gaussian function
def gaussian(x, A, mu, sigma):
    return A * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))

def fwhm(sigma):
    return 2.35482 * sigma

# Channel map
mapfile = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/CE_LD/chn_mapping.csv"
dmap = {}
with open(mapfile, "r") as f:
    for line in f:
        if "femb" in line:
            continue
        parts = line.strip().split(",")
        chno = int(parts[6])
        if len(parts[12]) >= 0:
            sipmno = parts[12][0:3] + "_" + parts[9] + "_" + parts[11] + f"_CH{chno:02d}_FNL" + parts[4]
            dmap[chno] = sipmno

# Directories
data_dir = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/SiPM_trigger_data"
output_dir = os.path.join(data_dir, "trigger_plot")
os.makedirs(output_dir, exist_ok=True)
results_hdf5 = os.path.join(data_dir, "trigger_analysis.hdf5")

# Date range
start_date = datetime(2025, 5, 5, tzinfo=pytz.timezone("America/New_York"))
end_date = datetime(2025, 7, 25, tzinfo=pytz.timezone("America/New_York"))

# Group files by date
files = sorted([f for f in os.listdir(data_dir) if f.endswith(".hdf5")])
file_groups = defaultdict(dict)
for f in files:
    if "_trigger" in f:
        parts = f.split("_")
        femb = parts[0][-1]
        date_str = parts[1]
        try:
            date = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=pytz.timezone("America/New_York"))
            if start_date <= date <= end_date:
                file_groups[date_str][f"femb{femb}"] = os.path.join(data_dir, f)
        except ValueError:
            continue

# Data storage
gain_data = defaultdict(list)  # (hour, gain, gain_idx)
norm_gain_data = defaultdict(list)  # (hour, norm_gain)
envelope_data = defaultdict(list)  # (day, envelope_peak)
res_data = defaultdict(list)  # (day, hour, resolution)
norm_res_data = defaultdict(list)  # (day, norm_resolution)
snr_data = defaultdict(list)  # (day, hour, snr)
fitted_centers_data = defaultdict(list)  # (day, hour, centers)
fitted_amplitudes_data = defaultdict(list)  # (day, hour, amplitudes)
reference_gain = defaultdict(dict)  # per channel, per hour
reference_res = defaultdict(dict)  # per channel, per day

# Processing FEMB files
first_timestamp = None
for date, paths in sorted(file_groups.items()):
    print(f"Processing date: {date}")
    if "femb1" not in paths or "femb2" not in paths:
        print(f"  Skipping date {date}, missing uFEMB1 or uFEMB2")
        continue

    for ufemb_id in [1, 2]:
        hdf5_fp = paths[f"femb{ufemb_id}"]
        with h5py.File(hdf5_fp, "r") as f:
            fns = f.get("file_analyzed", [])
            if len(fns) == 0:
                continue

            fns = sorted([fn.decode("utf-8") for fn in fns])
            fn0 = fns[0]
            ts0 = int(fn0[fn0.find(".tana") - 32:fn0.find(".tana")])
            dt0 = datetime.strptime(fn0[7:21], "%Y%m%d_%H_%M").replace(tzinfo=pytz.timezone("America/New_York"))
            dtt0 = int(dt0.timestamp())
            if first_timestamp is None:
                first_timestamp = dtt0
            day = dt0.toordinal()

            for ch in range(32):
                ch_global = (ufemb_id - 1) * 32 + ch
                if ch_global not in dmap:
                    continue
                name = dmap[ch_global]
                if "OPEN" in name:
                    continue

                hv_prefix = name[:3]  # HV1, HV2, HV3

                dset = f.get(f"CH{ch:02d}")
                if dset is None or len(dset) == 0:
                    continue

                ts, ds = zip(*dset)
                ts = np.array(ts) - ts0 * 10
                ds = np.array(ds)

                # Segment by jump
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

                for xi in range(len(subds)):
                    if len(subds[xi]) < 20:
                        continue

                    dtt00 = dtt0 + int(subts[xi][0] // 1e9)
                    dt = datetime.fromtimestamp(dtt00, tz=pytz.timezone("America/New_York"))
                    hour = (dtt00 - first_timestamp) / 3600.0  # Hours since start
                    print(f"Channel {ch_global}, Segment timestamp: {dt}, Hour since start: {hour:.2f}")
                    target_hours = [0, 8, 21]
                    allowed_hours = 1.0  # ±60 minutes = ±1 hour
                    current_hour = hour % 24
                    if not any(abs(current_hour - h) <= allowed_hours for h in target_hours):
                        print(f"  Skipping segment, not within ±1h of 00h, 08h, or 21h")
                        continue

                    vbinw = 1
                    counts, bin_edges = np.histogram(subds[xi], bins=range(int(min(subds[xi])), int(max(subds[xi])) + vbinw, vbinw))
                    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
                    peaks, _ = find_peaks(counts, prominence=20, distance=30)
                    print(f"  Channel {ch_global}, Peaks detected: {len(peaks)}")

                    fitted_centers, fitted_sigmas, fitted_amplitudes = [], [], []
                    for peak_idx in peaks[:4]:  # Limit to first 4 peaks
                        center = bin_centers[peak_idx]
                        if hv_prefix == "HV1":
                            win_half = 17
                        elif hv_prefix == "HV2":
                            win_half = 37
                        else:  # HV3
                            win_half = 50

                        window = (bin_centers > center - win_half) & (bin_centers < center + win_half)
                        x_fit = bin_centers[window]
                        y_fit = counts[window]
                        if len(x_fit) < 5:
                            continue

                        try:
                            p0 = [np.max(y_fit), center, (x_fit[-1] - x_fit[0]) / 6]
                            popt, _ = curve_fit(gaussian, x_fit, y_fit, p0=p0)
                            fitted_amplitudes.append(popt[0])
                            fitted_centers.append(popt[1])
                            fitted_sigmas.append(popt[2])
                        except:
                            continue

                    if len(fitted_centers) < 4:
                        print(f"  Channel {ch_global}, Skipping: Only {len(fitted_centers)} fitted centers")
                        continue

                    # Calculate gains
                    gains = [fitted_centers[2] - fitted_centers[1], fitted_centers[3] - fitted_centers[2]]
                    fwhm_p0 = fwhm(fitted_sigmas[0])
                    fwhm_p1 = fwhm(fitted_sigmas[1])

                    # Resolution: gain/FWHM(P1)
                    res = [g / fwhm_p1 if fwhm_p1 > 0 else np.nan for g in gains]

                    # SNR: peak_adc(P1)/FWHM(P0)
                    snr = fitted_centers[1] / fwhm_p0 if fwhm_p0 > 0 else np.nan

                    # Envelope fit
                    if len(fitted_centers) >= 2:
                        envelope_peak = max(fitted_centers[:2])  # Default to max of first two centers
                        try:
                            x_env = np.array(range(len(fitted_centers)))
                            y_env = np.array(fitted_centers)
                            p0_env = [np.max(y_env), np.argmax(y_env), 1.0]
                            popt_env, _ = curve_fit(gaussian, x_env, y_env, p0=p0_env)
                            if popt_env[0] > 0:
                                envelope_peak = popt_env[0]
                        except:
                            pass
                        envelope_data[ch_global].append((day, envelope_peak))

                    for gain_idx, gain in enumerate(gains):
                        gain_data[ch_global].append((hour, gain, gain_idx))
                        print(f"  Channel {ch_global}, Day {day}, Hour {hour:.2f}, Gain{gain_idx+2}: {gain:.2f}")
                    for r in res:
                        res_data[ch_global].append((day, hour, r))
                    snr_data[ch_global].append((day, hour, snr))
                    fitted_centers_data[ch_global].append((day, hour, fitted_centers))
                    fitted_amplitudes_data[ch_global].append((day, hour, fitted_amplitudes))

# Compute references for normalization
for ch in gain_data:
    gvals = np.array(gain_data[ch])  # (hour, gain, gain_idx)
    for target_hour in [0, 8, 21]:
        hour_mask = np.abs((gvals[:, 0] % 24) - target_hour) <= 1.0  # ±60 minutes in hours
        if np.any(hour_mask):
            gains_hour = gvals[hour_mask, 1]
            reference_gain[ch][target_hour] = np.mean(gains_hour) if len(gains_hour) > 0 else 1.0

for ch in res_data:
    rvals = np.array(res_data[ch])  # (day, hour, res)
    days = np.unique(rvals[:, 0])
    for day in days:
        mask = rvals[:, 0] == day
        if np.any(mask):
            res_day = rvals[mask, 2]
            reference_res[ch][day] = np.mean(res_day) if len(res_day) > 0 else 1.0

# Normalize gain and resolution
for ch in gain_data:
    for hour, g, i in gain_data[ch]:
        target_hour = min([0, 8, 21], key=lambda h: abs((hour % 24) - h))
        ref = reference_gain[ch].get(target_hour, 1.0)
        norm_gain_data[ch].append((hour, g / ref if ref else g))
for ch in res_data:
    for day, hour, r in res_data[ch]:
        ref = reference_res[ch].get(day, 1.0)
        norm_res_data[ch].append((day, r / ref if ref else r))

# Save results and plots
with h5py.File(results_hdf5, "w") as hf:
    for hv_prefix in ["HV1", "HV2", "HV3"]:
        hv_group = hf.create_group(hv_prefix)
        for ch in sorted(gain_data.keys()):
            if dmap[ch].startswith(hv_prefix):
                ch_group = hv_group.create_group(f"CH{ch:02d}")
                ch_group.create_dataset("gain", data=np.array(gain_data[ch], dtype=float))
                ch_group.create_dataset("norm_gain", data=np.array(norm_gain_data[ch], dtype=float))
                ch_group.create_dataset("res", data=np.array(res_data[ch], dtype=float))
                ch_group.create_dataset("norm_res", data=np.array(norm_res_data[ch], dtype=float))
                ch_group.create_dataset("snr", data=np.array(snr_data[ch], dtype=float))
                ch_group.create_dataset("envelope", data=np.array(envelope_data[ch], dtype=float))

                # Store only the first 4 fitted centers and amplitudes, padded to length 4
                max_peaks = 4
                centers_data = []
                for d, h, c in fitted_centers_data[ch]:
                    padded_centers = (c[:max_peaks] + [np.nan] * max_peaks)[:max_peaks]
                    centers_data.append([d, h] + padded_centers)
                ch_group.create_dataset("fitted_centers", data=np.array(centers_data, dtype=float))

                amplitudes_data = []
                for d, h, a in fitted_amplitudes_data[ch]:
                    padded_amplitudes = (a[:max_peaks] + [np.nan] * max_peaks)[:max_peaks]
                    amplitudes_data.append([d, h] + padded_amplitudes)
                ch_group.create_dataset("fitted_amplitudes", data=np.array(amplitudes_data, dtype=float))

        # Gain and Normalized Gain Plot
        for ch in sorted(gain_data.keys()):
            if not dmap[ch].startswith(hv_prefix):
                continue
            fig_gain, axs_gain = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
            fig_gain.suptitle(f"Channel {ch} ({dmap[ch]}) - Gain")
            for idx, color in enumerate(["green", "red"]):
                vals = [(h, g) for h, g, gi in gain_data[ch] if gi == idx]
                if vals:
                    h, g = zip(*vals)
                    axs_gain[0].scatter(h, g, s=30, color=color, label=f"Gain{idx+2}")
            axs_gain[0].set_ylabel("Gain")
            axs_gain[0].legend()
            axs_gain[0].grid()

            for target_hour, color in zip([0, 8, 21], ["blue", "orange", "purple"]):
                vals = [(h, g) for h, g in norm_gain_data[ch] if abs((h % 24) - target_hour) <= 1.0]
                if vals:
                    h, g = zip(*vals)
                    axs_gain[1].scatter(h, g, s=30, color=color, label=f"NormGain@{target_hour}h")
            axs_gain[1].set_ylabel("Norm Gain")
            axs_gain[1].set_ylim(0.9,1.1)
            axs_gain[1].set_xlabel("Hours")
            axs_gain[1].legend()
            axs_gain[1].grid()

            save_path_gain = os.path.join(output_dir, f"CH{ch:02d}_gain.png")
            fig_gain.tight_layout()
            plt.figure(fig_gain.number)
            plt.savefig(save_path_gain)
            plt.close(fig_gain)
            print(f"Saved gain plot: {save_path_gain}")

        # Resolution and Normalized Resolution Plot
        for ch in sorted(gain_data.keys()):
            if not dmap[ch].startswith(hv_prefix):
                continue
            fig_res, axs_res = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
            fig_res.suptitle(f"Channel {ch} ({dmap[ch]}) - Resolution")
            for hour, color in zip([0, 8, 21], ["blue", "orange", "purple"]):
                vals = [(day + hour/24, r) for day, h, r in res_data[ch] if abs((h % 24) - hour) <= 1.0]
                if vals:
                    d, r = zip(*vals)
                    axs_res[0].scatter(d, r, s=30, color=color, label=f"Res@{hour}h")
            axs_res[0].set_ylabel("Resolution")
            axs_res[0].legend()
            axs_res[0].grid()

            if norm_res_data[ch]:
                d, r = zip(*[(day, r) for day, r in norm_res_data[ch]])
                axs_res[1].scatter(d, r, s=30, color="magenta")
            axs_res[1].set_ylabel("Norm Resolution")
            axs_res[1].set_ylim(0.9,1.1)
            axs_res[1].set_xlabel("Days")
            axs_res[1].grid()

            save_path_res = os.path.join(output_dir, f"CH{ch:02d}_res.png")
            fig_res.tight_layout()
            plt.figure(fig_res.number)
            plt.savefig(save_path_res)
            plt.close(fig_res)
            print(f"Saved resolution plot: {save_path_res}")

        # Envelope Plot
        for ch in sorted(gain_data.keys()):
            if not dmap[ch].startswith(hv_prefix):
                continue
            fig_env, ax_env = plt.subplots(figsize=(10, 4))
            fig_env.suptitle(f"Channel {ch} ({dmap[ch]}) - Envelope Peaks")
            if envelope_data[ch]:
                d, p = zip(*envelope_data[ch])
                ax_env.scatter(d, p, s=30, color="cyan")
            ax_env.set_ylabel("Envelope Peak")
            ax_env.set_xlabel("Days")
            ax_env.grid()

            save_path_env = os.path.join(output_dir, f"CH{ch:02d}_envelope.png")
            fig_env.tight_layout()
            plt.figure(fig_env.number)
            plt.savefig(save_path_env)
            plt.close(fig_env)
            print(f"Saved envelope plot: {save_path_env}")

        # SNR Plot
        for ch in sorted(gain_data.keys()):
            if not dmap[ch].startswith(hv_prefix):
                continue
            fig_snr, ax_snr = plt.subplots(figsize=(10, 4))
            fig_snr.suptitle(f"Channel {ch} ({dmap[ch]}) - SNR")
            for hour, color in zip([0, 8, 21], ["blue", "orange", "purple"]):
                vals = [(day + hour/24, s) for day, h, s in snr_data[ch] if abs((h % 24) - hour) <= 1.0]
                if vals:
                    d, s = zip(*vals)
                    ax_snr.scatter(d, s, s=30, color=color, label=f"SNR@{hour}h")
            ax_snr.set_ylabel("SNR")
            ax_snr.set_xlabel("Day")
            ax_snr.legend()
            ax_snr.grid()

            save_path_snr = os.path.join(output_dir, f"CH{ch:02d}_snr.png")
            fig_snr.tight_layout()
            plt.figure(fig_snr.number)
            plt.savefig(save_path_snr)
            plt.close(fig_snr)
            print(f"Saved SNR plot: {save_path_snr}")

print(f"All results saved to {results_hdf5}")
