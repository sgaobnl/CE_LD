# -*- coding: utf-8 -*-
"""
Include Gaussian fitting for detected peaks, compute correlated noise (CN),
store CN and Gaussian parameters in HDF5.
IMPROVED: Uses highest amplitude peak as 1-pe reference with validation.
UPDATED: Sum limited to 0.5 pe < N < 4.5 pe range for CN calculation.
"""

import numpy as np
import h5py
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from zoneinfo import ZoneInfo
import pytz
import os
from datetime import datetime
import sys
import matplotlib.pyplot as plt

# ----------------------------
# Configuration
# ----------------------------
fm = "/data/disk1/koloina/CN/SiPM/chn_mapping.csv"
rootdir = "/data/disk1/koloina/CN/SiPM/"
drfp = "/data/disk1/koloina/CN/SiPM/New_Corr_noise_improved_final.hdf5"
log_file = os.path.join(rootdir, "processed_files.log")

print(f"Channel mapping file: {fm}")

# ----------------------------
# Load channel mapping
# ----------------------------
dmap = {}
if os.path.isfile(fm):
    with open(fm, "r") as f:
        for line in f:
            if "femb" in line:
                continue
            tmps = line.strip().split(",")
            chno = int(tmps[6])
            if len(tmps[12]) >= 0:
                sipmno = tmps[12][0:3] + "_" + tmps[9] + "_" + tmps[11] + "_" + "CH%02d" % chno + "_FNL" + tmps[4]
                dmap[chno] = sipmno
else:
    print(f"{fm} doesn't exist")
    sys.exit()

print("Channel mapping loaded.")

# ----------------------------
# HDF5 creation
# ----------------------------
def create_grp_hdf5(hdf5_fp):
    if not os.path.exists(hdf5_fp):
        with h5py.File(hdf5_fp, 'w') as f:
            maxshape = (None,)
            for chno, sipmno in dmap.items():
                if 'OPEN' not in sipmno:
                    f.create_group(sipmno)
            dt = h5py.string_dtype(encoding='utf-8')
            f.create_dataset("file_analyzed", shape=(0,), maxshape=maxshape, dtype=dt, chunks=True)
        print("HDF5 file and groups created.")

create_grp_hdf5(drfp)

# ----------------------------
# Gaussian function
# ----------------------------
def gaussian(x, amp, mu, sigma):
    return amp * np.exp(-(x - mu)**2 / (2 * sigma**2))

# ----------------------------
# Logging function
# ----------------------------
def write_to_log(msg):
    with open(log_file, "a") as lf:
        lf.write(msg + "\n")

# ----------------------------
# Append data to HDF5
# ----------------------------
def append_data(hdf5_fp, sipmno, dsetn, dsetd, attrsd):
    with h5py.File(hdf5_fp, 'a') as f:
        subgrp = f['/' + sipmno]
        if dsetn not in subgrp:
            dt = np.dtype([
                ("sum_Y", "f4"),
                ("sum_XY", "f4"),
                ("first_mu", "f4"),
                ("CN", "f4"),
                ("Gaussian_Amp", h5py.vlen_dtype(np.float32)),
                ("Gaussian_Mu", h5py.vlen_dtype(np.float32)),
                ("Gaussian_Sigma", h5py.vlen_dtype(np.float32))
            ])
            data = np.array([(dsetd["sum_Y"], dsetd["sum_XY"], dsetd["first_mu"], dsetd["CN"],
                              dsetd["Gaussian_Amp"], dsetd["Gaussian_Mu"], dsetd["Gaussian_Sigma"])], dtype=dt)
            subgrp.create_dataset(dsetn, data=data)
            for k, v in attrsd.items():
                subgrp[dsetn].attrs[k] = v

def append_anaed_fp(hdf5_fp, anafp):
    with h5py.File(hdf5_fp, 'a') as f:
        dset = f["file_analyzed"]
        old_size = dset.shape[0]
        dset.resize((old_size + 1,))
        dset[old_size] = anafp

def filter_anaed_file(hdf5_fp, anafp):
    with h5py.File(hdf5_fp, 'r') as f:
        fns = f["file_analyzed"][:]
        for fn in fns:
            if (anafp in str(fn)) and (datetime.now().strftime("%Y%m%d") not in str(fn)):
                return True
        return False

# ----------------------------
# Main processing loop
# ----------------------------
for _, dirs, _ in os.walk(rootdir):
    break

rstdirs = [d for d in dirs if "Result_" in d]
print("Results folders found:", rstdirs)
write_to_log(f"Results folders found: {rstdirs}")

for subdir in rstdirs:
    rst_dir = os.path.join(rootdir, subdir)
    for ufemb_id in [1, 2]:
        hdf5_fp = os.path.join(rst_dir, f"uFEMB{ufemb_id}_{subdir[7:15]}_darkrate.hdf5")
        if not os.path.isfile(hdf5_fp):
            continue

        if filter_anaed_file(drfp, hdf5_fp):
            print(hdf5_fp, "already analyzed.")
            write_to_log(f"Skipped (already analyzed): {hdf5_fp}")
            continue

        print(f"Processing file: {hdf5_fp}")
        write_to_log(f"Processing file: {hdf5_fp}")

        with h5py.File(hdf5_fp, "r") as f:
            fns = f["file_analyzed"][:]
            fns.sort()
            fn0 = fns[0].decode('utf-8')
            postana = fn0.find(".ana")
            ts0 = int(fn0[postana - 32:postana])
            dt0 = datetime.strptime(fn0[7:21], "%Y%m%d_%H_%M").replace(tzinfo=ZoneInfo("America/New_York"))
            dtt0 = int(dt0.timestamp())

            for ch in range(32):
                key = f"CH{ch:02d}"
                dn = dmap.get((ufemb_id - 1) * 32 + ch, None)
                if dn is None or "OPEN" in dn:
                    continue

                print(f"  Channel {ch:02d}, SiPM {dn}")
                write_to_log(f"  Channel {ch:02d}, SiPM {dn}")

                data = f[key][:]
                if len(data) == 0:
                    continue

                ts, ds = zip(*data)
                ts = np.array(ts) - ts0 * 10
                h2s = 3600
                vbinw = 10
                tlen = int(ts[-1])

                for hi in range(int(tlen // (1e9 * h2s)) + 1):
                    subts = ts[(ts > hi * h2s * 1e9) & (ts <= (hi + 1) * h2s * 1e9)]
                    if len(subts) == 0:
                        continue

                    dtt00 = dtt0 + hi * 3600
                    easten = pytz.timezone("America/New_York")
                    dt = datetime.fromtimestamp(dtt00, tz=easten)

                    print(f"    Processing hour starting at {dt.strftime('%Y-%m-%d %H:%M')}")
                    write_to_log(f"    Processing hour starting at {dt.strftime('%Y-%m-%d %H:%M')}")

                    subts_pos0 = np.where(ts == subts[0])[0][0]
                    subds = ds[subts_pos0: subts_pos0 + len(subts)]

                    # Histogram for darkrate amplitude distribution
                    counts, bin_edges = np.histogram(subds, bins=range(min(subds), max(subds) + vbinw, vbinw))
                    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

                    # === Detect peaks ===
                    peaks, _ = find_peaks(counts, prominence=20, distance=3)
                    if len(peaks) == 0:
                        print(f"      No peaks detected, skipping this hour")
                        write_to_log(f"      No peaks detected for hour {dt.strftime('%Y-%m-%d %H:%M')}")
                        continue

                    # === Gaussian Fitting with Validation ===
                    peak_centers = bin_centers[peaks]
                    peak_heights = counts[peaks]
                    gaussian_params = []
                    valid_fits = []

                    for peak_idx, peak in enumerate(peak_centers):
                        window = 50
                        mask = (bin_centers >= peak - window) & (bin_centers <= peak + window)
                        x_fit, y_fit = bin_centers[mask], counts[mask]
                        
                        # Skip if insufficient data points
                        if len(x_fit) < 5:
                            continue
                        
                        try:
                            p0 = [peak_heights[peak_idx], peak, vbinw]
                            popt, pcov = curve_fit(gaussian, x_fit, y_fit, p0=p0, maxfev=10000)
                            amp, mu, sigma = popt
                            
                            # === VALIDATION CHECKS ===
                            # 1. Check if fit parameters are reasonable
                            if amp <= 0 or sigma <= 0 or sigma > 100:
                                print(f"      Invalid fit parameters: amp={amp}, sigma={sigma}")
                                continue
                            
                            # 2. Check if mu is within reasonable range
                            if mu < 0 or mu > 300:
                                print(f"      Unreasonable mu value: {mu}")
                                continue
                            
                            # 3. Check fit quality using covariance
                            if np.any(np.diag(pcov) > 1e6):
                                print(f"      Poor fit quality (high covariance)")
                                continue
                            
                            # 4. Check R-squared goodness of fit
                            y_pred = gaussian(x_fit, amp, mu, sigma)
                            ss_res = np.sum((y_fit - y_pred)**2)
                            ss_tot = np.sum((y_fit - np.mean(y_fit))**2)
                            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                            
                            if r_squared < 0.5:
                                print(f"      Poor R² value: {r_squared:.3f}")
                                continue
                            
                            gaussian_params.append((amp, mu, sigma))
                            valid_fits.append((amp, mu, sigma, r_squared))
                            
                        except RuntimeError as e:
                            print(f"      Fit failed: {e}")
                            continue
                        except Exception as e:
                            print(f"      Unexpected error in fitting: {e}")
                            continue

                    # === Additional validation before CN calculation ===
                    if len(gaussian_params) == 0:
                        print(f"      No valid Gaussian fits, skipping this hour")
                        write_to_log(f"      No valid fits for hour {dt.strftime('%Y-%m-%d %H:%M')}")
                        continue

                    # Sort by AMPLITUDE to get the highest peak (1-photoelectron peak)
                    gaussian_params = sorted(gaussian_params, key=lambda x: x[0], reverse=True)
                    first_amp, first_mu, first_sigma = gaussian_params[0]
                    
                    print(f"      Selected 1-pe peak: amp={first_amp:.1f}, mu={first_mu:.1f}, sigma={first_sigma:.1f}")

                    # === Validate first_mu before CN calculation ===
                    if first_mu < 90:  # Adjust threshold based on your expected values
                        print(f"      first_mu too small ({first_mu:.2f}), skipping")
                        write_to_log(f"      Invalid first_mu={first_mu:.2f} for {dt.strftime('%Y-%m-%d %H:%M')}")
                        continue

                    # === Calculate CN with safety checks ===
                    # Apply the constraint: sum only over 0.5 pe < N < 4.5 pe
                    lower_bound = 0.5 * first_mu
                    upper_bound = 4.5 * first_mu
                    
                    # Create mask for the valid range
                    mask = (bin_centers >= lower_bound) & (bin_centers <= upper_bound)
                    
                    # Filter X and Y arrays
                    X_filtered = bin_centers[mask]
                    Y_filtered = counts[mask]
                    
                    # Calculate sums only over the filtered range
                    sum_Y = np.sum(Y_filtered)
                    sum_XY = np.sum(X_filtered * Y_filtered)
                    
                    # Check for minimum counts in filtered range
                    min_counts_threshold = 100  # Adjust based on your data
                    if sum_Y == 0:
                        print(f"      Zero counts in 0.5-4.5 pe range, skipping")
                        write_to_log(f"      Zero counts in filtered range for {dt.strftime('%Y-%m-%d %H:%M')}")
                        continue
                    elif sum_Y < min_counts_threshold:
                        print(f"      Warning: Low statistics in filtered range (N={sum_Y:.0f})")
                        write_to_log(f"      Low statistics warning: sum_Y={sum_Y:.0f} for {dt.strftime('%Y-%m-%d %H:%M')}")

                    CN = sum_XY / (first_mu * sum_Y) - 1
                    
                    print(f"      Filtered range: [{lower_bound:.1f}, {upper_bound:.1f}] ADC")
                    print(f"      Counts in range: {sum_Y:.0f}")

                    # === Validate CN value ===
                    if not np.isfinite(CN) or CN < 0 or CN > 2:
                        print(f"      Invalid CN value: {CN:.3f}, skipping")
                        write_to_log(f"      Invalid CN={CN:.3f} for {dt.strftime('%Y-%m-%d %H:%M')}")
                        continue

                    # Optional: Log fit quality
                    if valid_fits:
                        r2 = valid_fits[0][3]
                        print(f"      CN={CN:.3f}, first_mu={first_mu:.1f}, R²={r2:.3f}")
                        write_to_log(f"      CN={CN:.3f}, first_mu={first_mu:.1f}, R²={r2:.3f}")

                    # === Save Results ===
                    attrsd = {
                        "Start_TS": subts[0] + ts0, 
                        "End_TS": subts[-1] + ts0,
                        "First_Peak_R2": valid_fits[0][3] if valid_fits else -1,
                        "PE_Range_Lower": lower_bound,
                        "PE_Range_Upper": upper_bound
                    }
                    dsetd = {
                        "sum_Y": sum_Y,
                        "sum_XY": sum_XY,
                        "first_mu": first_mu,
                        "CN": CN,
                        "Gaussian_Amp": np.array([p[0] for p in gaussian_params], dtype=np.float32),
                        "Gaussian_Mu": np.array([p[1] for p in gaussian_params], dtype=np.float32),
                        "Gaussian_Sigma": np.array([p[2] for p in gaussian_params], dtype=np.float32),
                    }
                    append_data(drfp, dn, dt.strftime("%Y_%m_%d_%H"), dsetd, attrsd)

        append_anaed_fp(drfp, hdf5_fp)
        print(f"Finished processing: {hdf5_fp}")
        write_to_log(f"Finished processing: {hdf5_fp}")
