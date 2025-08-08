#!/usr/bin/env python3

import numpy as np
import os
import h5py
from datetime import datetime, timezone
import pytz
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# ----------------------------
# Gaussian function
# ----------------------------
def gaussian(x, A, mu, sigma):
    return A * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))

# ----------------------------
# Channel mapping
# ----------------------------
def load_channel_mapping(fm, femb_number):
    """
    Load channel mapping for a specific FEMB number.
    
    Args:
        fm (str): Path to the channel mapping CSV file.
        femb_number (int): FEMB number (0 for uFEMB1, 1 for uFEMB2).
    
    Returns:
        dict: Dictionary mapping chn_in_data# to SiPM info string.
    """
    dmap = {}
    if not os.path.isfile(fm):
        raise FileNotFoundError(f"{fm} doesn't exist")
    
    with open(fm, "r") as f:
        for line in f:
            if "femb" in line:  # Skip header
                continue
            tmps = line.strip().split(",")
            try:
                current_femb = int(tmps[0])  # femb#
                chn_in_data = int(tmps[3])   # chn_in_data#
                chn = int(tmps[6])           # CHN
                sipm = tmps[12]              # SiPM#
                con8 = tmps[9]               # 8-pin CON
                con8_pin = tmps[11]          # 8-pin CON pin#
                fnl_lot = tmps[4]            # FNL lot#
                hv = tmps[13]                # HV
                
                # Filter by femb# and exclude HV1 for uFEMB2
                if current_femb == femb_number:
                    if femb_number == 1 and hv == "HV1(P15)":  # Skip HV1 for uFEMB2
                        continue
                    # Handle OPEN channels
                    sipm_prefix = sipm[:3] if sipm != "OPEN" else "OPEN"
                    sipmno = f"{sipm_prefix}_{con8}_{con8_pin}_CH{chn:02d}_FNL{fnl_lot}"
                    dmap[chn_in_data] = sipmno
            except (IndexError, ValueError) as e:
                print(f"Warning: Skipping invalid line: {line.strip()} - {e}")
                continue
    
    return dmap

fm = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/CE_LD/chn_mapping.csv"
try:
    # Load mappings for uFEMB1 (femb#=0) and uFEMB2 (femb#=1)
    dmap_ufemb1 = load_channel_mapping(fm, femb_number=0)
    dmap_ufemb2 = load_channel_mapping(fm, femb_number=1)
except FileNotFoundError as e:
    print(e)
    exit(1)

# ----------------------------
# Root directory
# ----------------------------
rootdir = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/SiPM"
hdf5_output = os.path.join(rootdir, "AnalysisResults.hdf5")

# Initialize output file
with h5py.File(hdf5_output, "w") as f:
    f.attrs["description"] = "SiPM Gain/Resolution/SNR/Envelope Analysis Results"

# ----------------------------
# Main Analysis
# ----------------------------
for root, dirs, files in os.walk(rootdir):
    break

rstdirs = [onedir for onedir in dirs if "Result_" in onedir]

for subdir in rstdirs:
    rst_dir = os.path.join(rootdir, subdir)
    print(f"\n--- Processing: {rst_dir} ---")

    for ufemb_id in [1, 2]:
        print(f"\n→ Processing uFEMB{ufemb_id}")

        # Select the appropriate channel mapping
        dmap = dmap_ufemb1 if ufemb_id == 1 else dmap_ufemb2

        for local_ch in range(32):  # Iterate over chn_in_data# (0-31)
            dn = dmap.get(local_ch, "Unknown")
            if "OPEN" in dn or dn == "Unknown":
                continue

            all_subts, all_subds = [], []
            hdf5_fp = os.path.join(rst_dir, f"uFEMB{ufemb_id}_{subdir[7:15]}_trigger.hdf5")
            if not os.path.isfile(hdf5_fp):
                continue

            with h5py.File(hdf5_fp, "r") as f:
                fns = f.get("file_analyzed", [])
                if len(fns) == 0:
                    continue
                fns = sorted([fn.decode('utf-8') for fn in fns])
                fn0 = fns[0]
                ts0 = int(fn0[fn0.find(".tana") - 32:fn0.find(".tana")])
                dt0 = datetime.strptime(fn0[7:7+14], "%Y%m%d_%H_%M").replace(tzinfo=ZoneInfo("America/New_York"))
                dtt0 = int(dt0.timestamp())

                key = f"CH{local_ch:02d}"
                data = f.get(key, None)
                if data is None or len(data) == 0:
                    continue

                ts, ds = zip(*data)
                ts = np.array(ts) - ts0 * 10
                ds = np.array(ds)

                diffs = ts[1:] - ts[:-1]
                jumps = np.where(diffs > 1e9)[0]
                prev = 0
                for idx in jumps:
                    subt = ts[prev:idx+1].copy()
                    subd = ds[prev:idx+1].copy()
                    poss = np.where(subd > 30)[0]
                    if len(poss) < 10:
                        prev = idx + 1
                        continue
                    posb, pose = poss[0], poss[-1]
                    all_subts.append(subt[posb:pose])
                    all_subds.append(subd[posb:pose])
                    prev = idx + 1
                all_subts.append(ts[prev:].copy())
                all_subds.append(ds[prev:].copy())

            if len(all_subts) == 0:
                print(f"{dn} (uFEMB{ufemb_id}) → No triggers found.")
                continue

            print(f"Found {len(all_subts)} triggers for {dn} (uFEMB{ufemb_id})")

            for xi in range(len(all_subts)):
                sub_t = all_subts[xi]
                sub_d = all_subds[xi]
                if len(sub_d) == 0:
                    continue

                dtt00 = dtt0 + int(sub_t[0] // 1e9)
                dt = datetime.fromtimestamp(dtt00, tz=pytz.timezone("America/New_York"))
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")

                vbinw = 1
                counts, bin_edges = np.histogram(sub_d, bins=range(int(min(sub_d)), int(max(sub_d)) + vbinw, vbinw))
                peaks, _ = find_peaks(counts, prominence=20, distance=30)
                bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
                
                #Initialisation of parameters 
                fitted_centers, fitted_sigmas, fitted_amplitudes, gauss_params = [], [], [], []
                hv_prefix = dn.split("_")[0]
                #Peak window fitting for the gaussian fit
                for peak_idx in peaks[0:4]:
                    center = bin_centers[peak_idx]
                    if hv_prefix == "HV1":
                        win_half = 17
                    elif hv_prefix == "HV2":
                        win_half = 37
                    else:
                        win_half = 50
                    window = (bin_centers > center - win_half) & (bin_centers < center + win_half)
                    x_fit, y_fit = bin_centers[window], counts[window]
                    if len(x_fit) < 5:
                        continue
                    try:
                        sigma_guess = (x_fit[-1] - x_fit[0]) / 6
                        p0 = [np.max(y_fit), center, sigma_guess]
                        p0, _ = curve_fit(gaussian, x_fit, y_fit, p0=p0)
                        gauss_params.append(p0)
                        fitted_amplitudes.append(p0[0])
                        fitted_centers.append(p0[1])
                        fitted_sigmas.append(p0[2])
                    except Exception:
                        continue
                        
                #Calculations of fwhm for later SNR and resolution calculations 
                fwhms = [2.355 * s for s in fitted_sigmas]

                #Resolution calculation
                res_values = [] #initialization
                for i in range(len(fitted_centers) - 1):
                    delta = fitted_centers[i + 1] - fitted_centers[i]
                    res_values.append((fwhms[1] / delta)*100 if fwhms[1] > 0 else np.nan) #the resolution is in %

                #SNR calculation
                if len(fitted_amplitudes) > 1 and len(fwhms) > 0 and fwhms[0] > 0:
                    snr = fitted_centers[1] / fwhms[0]
                else:
                    snr = np.nan

                # Envelope fit
                env_mu, env_sigma, env_fwhm = np.nan, np.nan, np.nan
                if len(fitted_centers) >= 3:
                    try:
                        def peak_envelope(x, A, mu, sigma):
                            return gaussian(x, A, mu, sigma)
                        p0_env = [max(fitted_amplitudes), np.mean(fitted_centers), np.std(fitted_centers)]
                        popt_env, _ = curve_fit(peak_envelope, fitted_centers, fitted_amplitudes, p0=p0_env)
                        env_mu, env_sigma = popt_env[1], popt_env[2]
                        env_fwhm = 2.355 * env_sigma
                    except Exception:
                        pass

                # Save results in HDF5
                with h5py.File(hdf5_output, "a") as fout:
                    grp_path = f"{dn}/uFEMB{ufemb_id}"
                    grp = fout.require_group(grp_path)
                    dset = grp.create_group(date_str)

                    dset.create_dataset("fitted_centers", data=np.array(fitted_centers))
                    dset.create_dataset("fitted_amplitudes", data=np.array(fitted_amplitudes))
                    dset.create_dataset("fitted_sigmas", data=np.array(fitted_sigmas))
                    dset.create_dataset("fwhms", data=np.array(fwhms))
                    dset.create_dataset("resolutions", data=np.array(res_values))
                    dset.create_dataset("snr", data=np.array([snr]))
                    dset.attrs["envelope_mu"] = env_mu
                    dset.attrs["envelope_sigma"] = env_sigma
                    dset.attrs["envelope_fwhm"] = env_fwhm

                print(f"Saved results for {dn} (uFEMB{ufemb_id}) at {date_str}")
