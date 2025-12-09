import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from zoneinfo import ZoneInfo
import pytz

# ----------------------------
# Channel mapping
# ----------------------------
def load_channel_mapping(fm, femb_number):
    dmap = {}
    if not os.path.isfile(fm):
        raise FileNotFoundError(f"{fm} doesn't exist")
    
    with open(fm, "r") as f:
        for line in f:
            if "femb" in line:
                continue
            tmps = line.strip().split(",")
            try:
                current_femb = int(tmps[0])
                chn_in_data = int(tmps[3])
                chn = int(tmps[6])
                sipm = tmps[12]
                con8 = tmps[9]
                con8_pin = tmps[11]
                fnl_lot = tmps[4]
                hv = tmps[13]
                if current_femb == femb_number:
                    if femb_number == 1 and hv == "HV1(P15)":
                        continue
                    sipm_prefix = sipm[:3] if sipm != "OPEN" else "OPEN"
                    sipmno = f"{sipm_prefix}_{con8}_{con8_pin}_CH{chn:02d}_FNL{fnl_lot}"
                    dmap[chn_in_data] = sipmno
            except (IndexError, ValueError):
                continue
    return dmap

# ----------------------------
# Gaussian function
# ----------------------------
def gaussian(x, amp, mu, sigma):
    return amp * np.exp(-(x - mu)**2 / (2 * sigma**2))

# ----------------------------
# Create result file
# ----------------------------
def create_output_hdf5(hdf5_fp, dmap1, dmap2):
    if not os.path.exists(hdf5_fp):
        with h5py.File(hdf5_fp, 'w') as f:
            for dmap in [dmap1, dmap2]:
                for ch, sipmno in dmap.items():
                    if 'OPEN' not in sipmno:
                        f.create_group(sipmno)
        print("Output file created with groups.")

# ----------------------------
# Save results
# ----------------------------
def save_peak_and_gain(hdf5_fp, sipmno, dt_str, peaks, gains, ts_range):
    with h5py.File(hdf5_fp, 'a') as f:
        grp = f[sipmno]
        peak_dtype = np.dtype([("mu", "f4"), ("sigma", "f4"), ("amp", "f4")])
        gain_dtype = np.dtype([("gain", "f4")])
        if dt_str in grp:
            del grp[dt_str]
        subgrp = grp.create_group(dt_str)
        subgrp.create_dataset("peaks", data=np.array(peaks, dtype=peak_dtype))
        subgrp.create_dataset("gains", data=np.array(gains, dtype=gain_dtype))
        subgrp.attrs["Start_TS"] = ts_range[0]
        subgrp.attrs["End_TS"] = ts_range[1]

# ----------------------------
# Main analysis
# ----------------------------
def process_files(rootdir, output_hdf5, dmap1, dmap2):
    for subdir in sorted(os.listdir(rootdir)):
        if not subdir.startswith("Result_"):
            continue
        rst_dir = os.path.join(rootdir, subdir)
        for ufemb_id in [1, 2]:
            hdf5_name = f"uFEMB{ufemb_id}_{subdir[7:15]}_darkrate.hdf5"
            hdf5_fp = os.path.join(rst_dir, hdf5_name)
            if not os.path.isfile(hdf5_fp):
                continue

            print(f"Processing {hdf5_fp}")
            dmap = dmap1 if ufemb_id == 1 else dmap2

            with h5py.File(hdf5_fp, "r") as f:
                file_keys = f["file_analyzed"][:]
                fn0 = file_keys[0].decode()
                ts0 = int(fn0[fn0.find(".ana") - 32:fn0.find(".ana")])
                dt0 = datetime.strptime(fn0[7:21], "%Y%m%d_%H_%M").replace(tzinfo=ZoneInfo("America/New_York"))
                dtt0 = int(dt0.timestamp())

                for local_ch in range(32):
                    chname = f"CH{local_ch:02d}"
                    if local_ch not in dmap:
                        continue
                    sipmno = dmap[local_ch]
                    if "OPEN" in sipmno or chname not in f:
                        continue

                    data = f[chname][:]
                    if len(data) == 0:
                        continue
                    ts, amps = zip(*data)
                    ts = np.array(ts) - ts0 * 10
                    amps = np.array(amps)

                    # Group by hour
                    for hi in range(int((ts[-1]) // (1e9 * 3600)) + 1):
                        start_ns = hi * 3600 * 1e9
                        end_ns = (hi + 1) * 3600 * 1e9
                        mask = (ts >= start_ns) & (ts < end_ns)
                        if not np.any(mask):
                            continue
                        amps_hour = amps[mask]

                        # Skip if average amplitude < 20
                        if np.mean(amps_hour) < 20:
                            continue

                        ts_range = (int(ts[mask][0] + ts0), int(ts[mask][-1] + ts0))
                        dt = datetime.fromtimestamp(dtt0 + hi * 3600, tz=ZoneInfo("America/New_York"))
                        dt_str = dt.strftime("%Y_%m_%d_%H")

                        # Histogram and peak finding
                        vbinw = 10
                        counts, bins = np.histogram(amps_hour, bins=range(min(amps_hour), max(amps_hour)+vbinw, vbinw))
                        bin_centers = 0.5 * (bins[:-1] + bins[1:])
                        peaks_idx, _ = find_peaks(counts, prominence=20, distance=3)
                        peak_centers = bin_centers[peaks_idx]
                        peak_heights = counts[peaks_idx]

                        fitted_peaks = []
                        for i, peak in enumerate(peak_centers):
                            mask = (bin_centers >= peak - 30) & (bin_centers <= peak + 30)
                            x_fit = bin_centers[mask]
                            y_fit = counts[mask]
                            try:
                                p0 = [peak_heights[i], peak, vbinw]
                                popt, _ = curve_fit(gaussian, x_fit, y_fit, p0=p0, maxfev=10000)
                                amp, mu, sigma = popt
                                fitted_peaks.append((mu, sigma, amp))
                            except RuntimeError:
                                continue

                        # Remove close peaks (mu difference < 100)
                        filtered = []
                        i = 0
                        while i < len(fitted_peaks):
                            mu1 = fitted_peaks[i][0]
                            if i+1 < len(fitted_peaks) and abs(fitted_peaks[i+1][0] - mu1) < 100:
                                i += 2
                                continue
                            filtered.append(fitted_peaks[i])
                            i += 1

                        # Compute gain: μ(i+1) - μ(i)
                        gains = []
                        for i in range(len(filtered)-1):
                            gain_val = filtered[i+1][0] - filtered[i][0]
                            gains.append((gain_val,))

                        # Save to output file
                        save_peak_and_gain(output_hdf5, sipmno, dt_str, filtered, gains, ts_range)

# ----------------------------
# Run everything
# ----------------------------
if __name__ == "__main__":
    rootdir = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/SiPM"
    output_hdf5 = os.path.join(rootdir, "Dark_analysis.hdf5")
    mapping_file = os.path.join(rootdir, "chn_mapping.csv")

    dmap_ufemb1 = load_channel_mapping(mapping_file, 0)
    dmap_ufemb2 = load_channel_mapping(mapping_file, 1)

    create_output_hdf5(output_hdf5, dmap_ufemb1, dmap_ufemb2)

    process_files(rootdir, output_hdf5, dmap_ufemb1, dmap_ufemb2)
