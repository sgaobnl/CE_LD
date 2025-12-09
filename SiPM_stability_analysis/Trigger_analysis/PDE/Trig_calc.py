#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import os
import h5py
from datetime import datetime
import pytz
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

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
# User paths
# ----------------------------
fm = "/data/disk1/koloina/waveform_fitting/chn_mapping.csv"
rootdir = "/data/disk1/koloina/waveform_fitting/SIPM/"
hdf5_output = os.path.join(rootdir, "trigger_pde_calc.hdf5")


# ----------------------------
# Load mappings
# ----------------------------
try:
    dmap_ufemb1 = load_channel_mapping(fm, femb_number=0)
    dmap_ufemb2 = load_channel_mapping(fm, femb_number=1)
except FileNotFoundError as e:
    print(e)
    raise SystemExit(1)


# ----------------------------
# Initialize output HDF5
# ----------------------------
with h5py.File(hdf5_output, "w") as f:
    f.attrs["description"] = "SiPM PDE values from fitted trigger peak amplitudes"


# ----------------------------
# Find Result directories
# ----------------------------
for root, dirs, files in os.walk(rootdir):
    break

rstdirs = [d for d in dirs if "Result_" in d]
if not rstdirs:
    print("No Result_ directories found under", rootdir)
    raise SystemExit(0)


# ----------------------------
# Main analysis loop
# ----------------------------
for subdir in sorted(rstdirs):

    rst_dir = os.path.join(rootdir, subdir)
    print(f"\n--- Processing {rst_dir} ---")

    for ufemb_id in [1, 2]:

        print(f"\n→ Processing uFEMB{ufemb_id}")

        dmap = dmap_ufemb1 if ufemb_id == 1 else dmap_ufemb2

        for local_ch in range(32):

            dn = dmap.get(local_ch, "Unknown")

            if "OPEN" in dn or dn == "Unknown":
                continue

            hdf5_fp = os.path.join(
                rst_dir,
                f"uFEMB{ufemb_id}_LED_{subdir[7:15]}.h5"
            )

            if not os.path.isfile(hdf5_fp):
                continue

            all_subts = []
            all_subds = []

            # ----------------------------
            # Read raw trigger data
            # ----------------------------
            with h5py.File(hdf5_fp, "r") as f:

                fns = f.get("file_analyzed", [])
                if len(fns) == 0:
                    continue

                fns = sorted([fn.decode("utf-8") for fn in fns])
                fn0 = fns[0]

                try:
                    ts0 = int(
                        fn0[
                            fn0.find(".tana") - 32 : fn0.find(".tana")
                        ]
                    )
                except Exception:
                    ts0 = 0

                try:
                    dt0 = datetime.strptime(
                        fn0[7:7 + 14], "%Y%m%d_%H_%M"
                    ).replace(
                        tzinfo=ZoneInfo("America/New_York")
                    )
                    dtt0 = int(dt0.timestamp())

                except Exception:
                    dtt0 = 0

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
                    subt = ts[prev:idx + 1].copy()
                    subd = ds[prev:idx + 1].copy()

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
                continue


            # ----------------------------
            # Analyze each trigger block
            # ----------------------------
            for xi in range(len(all_subts)):

                sub_t = all_subts[xi]
                sub_d = all_subds[xi]

                if len(sub_d) == 0:
                    continue

                dtt00 = dtt0 + int(sub_t[0] // 1e9) if dtt0 != 0 else 0

                dt_obj = datetime.fromtimestamp(
                    dtt00,
                    tz=pytz.timezone("America/New_York")
                ) if dtt00 != 0 else datetime.now()

                date_str = dt_obj.strftime("%Y-%m-%d_%H-%M-%S")


                # ----------------------------
                # Histogram
                # ----------------------------
                vmin = int(np.floor(np.min(sub_d)))
                vmax = int(np.ceil(np.max(sub_d)))

                if vmax <= vmin:
                    continue

                bins = range(vmin, vmax + 1)
                counts, bin_edges = np.histogram(sub_d, bins=bins)
                bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])


                # ----------------------------
                # Find peaks
                # ----------------------------
                peaks, _ = find_peaks(
                    counts,
                    prominence=20,
                    distance=30
                )

                peaks = list(peaks)

                idx0 = int(np.argmin(np.abs(bin_centers - 0.0)))
                if counts[idx0] > 0:
                    if len(peaks) == 0 or \
                       (bin_centers[peaks[0]] - bin_centers[idx0]) > 100:
                        peaks.insert(0, idx0)

                if len(peaks) == 0:
                    continue


                # ----------------------------
                # Gaussian fits
                # ----------------------------
                fitted_amplitudes = []

                hv_prefix = dn.split("_")[0] if "_" in dn else dn

                for i, peak_idx in enumerate(peaks):

                    center = bin_centers[peak_idx]

                    if i == 0 or hv_prefix == "HV1":
                        win_half = 17
                    elif hv_prefix == "HV2":
                        win_half = 37
                    else:
                        win_half = 50

                    mask = (
                        (bin_centers > center - win_half) &
                        (bin_centers < center + win_half)
                    )

                    x_fit = bin_centers[mask]
                    y_fit = counts[mask]

                    if len(x_fit) < 5 or np.sum(y_fit) < 5:
                        continue

                    try:
                        sigma_guess = max(
                            (x_fit[-1] - x_fit[0]) / 6.0,
                            0.5
                        )

                        p0 = [np.max(y_fit), center, sigma_guess]

                        popt, _ = curve_fit(
                            gaussian,
                            x_fit,
                            y_fit,
                            p0=p0,
                            maxfev=10000
                        )

                        fitted_amplitudes.append(popt[0])

                    except Exception:
                        continue

                if len(fitted_amplitudes) < 2:
                    continue


                # ----------------------------
                # PDE calculation
                # ----------------------------
                amps = np.array(fitted_amplitudes)

                A0 = amps[0]
                Atot = np.sum(amps)

                if A0 <= 0 or Atot <= 0:
                    continue

                pde = -np.log(A0 / Atot)


                # ----------------------------
                # Save results
                # ----------------------------
                with h5py.File(hdf5_output, "a") as fout:

                    grp_path = f"{dn}/uFEMB{ufemb_id}"

                    grp = fout.require_group(grp_path)

                    if date_str in grp:
                        continue

                    dset = grp.create_group(date_str)

                    dset.create_dataset(
                        "peak_amplitudes",
                        data=amps
                    )

                    dset.create_dataset(
                        "pde",
                        data=np.array([pde])
                    )

                print(
                    f"Saved PDE + amplitudes for "
                    f"{dn} (uFEMB{ufemb_id}) at {date_str}"
                )


print("\n✅ PDE extraction completed.")
print("Output saved to:")
print(hdf5_output)
