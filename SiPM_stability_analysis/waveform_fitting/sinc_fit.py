# -*- coding: utf-8 -*-
"""
Batch waveform sinc interpolation fit → structured HDF5 per Anaata folder
------------------------------------------------------------------------
- One HDF5 per Anaata folder: uFEMB1_LED_YYYYMMDD.h5
- Combines all .tana files in the folder
- Saves baseline-subtracted peaks as structured datasets per channel
- dtype: ("TS","i8"), ("Value","u2")
- Channels 0 and 16 skipped
- Interactive fit window selection only once per channel (reused automatically)
  → Stored globally in fit_windows_master.h5 and reused across all days
- Automatically processes all Anaata folders without stopping
- If all days are already processed, prompts user to re-enter fit windows
"""

import os
import glob
import pickle
import numpy as np
import h5py
import matplotlib.pyplot as plt

# ======== Input paths ========
rootp = "/data/disk1/koloina/waveform_fitting/SiPM_FEMB2/August/"

anaata_folders = sorted(
    glob.glob(os.path.join(rootp, "Anaata_*")),
    key=lambda f: os.path.basename(f).split("_")[1],
)

# ======== Dtype for structured HDF5 ========
dtype = np.dtype([("TS", "i8"), ("Value", "u2")])

# ======== Master fit window file ========
fit_master_fp = os.path.join(rootp, "fit_windows_master.h5")

def load_or_create_master_windows():
    """Load global fit windows or create default file."""
    windows = {}
    with h5py.File(fit_master_fp, 'a') as f:
        if "fit_windows" not in f:
            grp = f.create_group("fit_windows")
            for chi in range(32):
                grp.create_dataset(f"CH{chi:02d}", data=[-1.0, -1.0])
        for chi in range(32):
            xmin, xmax = f["fit_windows"][f"CH{chi:02d}"][:]
            if xmin >= 0 and xmax >= 0:
                windows[chi] = (float(xmin), float(xmax))
    return windows

def save_master_window(chi, xmin, xmax):
    """Save a new global fit window to master HDF5."""
    with h5py.File(fit_master_fp, 'a') as f:
        f["fit_windows"][f"CH{chi:02d}"][:] = [xmin, xmax]

# ======== Sinc interpolation ========
def sinc_interp(x, s, u, T=None, lanczos_a=8, neighbor_window_us=5):
    if T is None:
        T = x[1] - x[0]
    xmin = u.min() - neighbor_window_us
    xmax = u.max() + neighbor_window_us
    sel = (x >= xmin) & (x <= xmax)
    x_sel = x[sel]
    s_sel = s[sel]
    arg = (u[:, None] - x_sel[None, :]) / T
    sinc_matrix = np.sinc(arg)
    if lanczos_a is not None and lanczos_a > 0:
        sinc_matrix *= np.sinc(arg / lanczos_a)
    return sinc_matrix @ s_sel

# ======== HDF5 helper functions ========
def append_structured_data(hdf5_fp, tdszip, anafp):
    dt = h5py.string_dtype(encoding='utf-8')
    with h5py.File(hdf5_fp, 'a') as f:
        for chi in range(32):
            if not tdszip[chi]:
                continue
            newdata = np.array(tdszip[chi], dtype=dtype)
            dset = f[f"CH{chi:02d}"]
            old_size = dset.shape[0]
            dset.resize((old_size + newdata.shape[0],))
            dset[old_size:] = newdata

        nstring = np.array([anafp], dtype=dt)
        dset = f["file_analyzed"]
        old_size = dset.shape[0]
        dset.resize((old_size + nstring.shape[0],))
        dset[old_size:] = nstring

def filter_anaed_file(hdf5_fp, anafp):
    with h5py.File(hdf5_fp, 'r') as f:
        fns = f["file_analyzed"][:]
        return any(anafp in str(fn) for fn in fns)

# ======== MAIN PROCESSING LOOP ========
fit_windows = load_or_create_master_windows()
total_days = len(anaata_folders)
processed_days = 0
unprocessed_days = 0

for folder in anaata_folders:
    folder_name = os.path.basename(folder)
    date_str = folder_name.split("_")[1]
    hdf5_fp = os.path.join(rootp, f"uFEMB2_LED_{date_str}.h5")

    print(f"\n=== Processing {folder_name} ({processed_days + 1}/{total_days}) ===")

    # Create structured HDF5 if missing
    if not os.path.exists(hdf5_fp):
        with h5py.File(hdf5_fp, "w") as f:
            maxshape = (None,)
            for chi in range(32):
                f.create_dataset(f"CH{chi:02d}", shape=(0,), maxshape=maxshape,
                                 dtype=dtype, chunks=True)
            dt = h5py.string_dtype(encoding='utf-8')
            f.create_dataset("file_analyzed", shape=(0,), maxshape=maxshape,
                             dtype=dt, chunks=True)
        print(f"Created HDF5: {hdf5_fp}")

    tana_files = sorted(glob.glob(os.path.join(folder, "*.tana")))
    if not tana_files:
        print("No .tana files found, skipping.")
        continue

    new_files_found = False

    # --- Process all .tana files ---
    for fp in tana_files:
        fname = os.path.basename(fp)
        if filter_anaed_file(hdf5_fp, fname):
            continue  # skip already processed

        new_files_found = True
        with open(fp, "rb") as fs:
            datas = pickle.load(fs)

        if isinstance(datas, dict):
            channels = list(datas.keys())
        elif isinstance(datas, list):
            channels = list(range(len(datas)))
        else:
            raise TypeError(f"Unexpected datas type: {type(datas)}")

        tdszip = [[] for _ in range(32)]

        # --- Fit all channels ---
        for chi in channels:
            chi = int(chi)
            if chi in [0, 16] or len(datas[chi]) == 0:
                continue

            if chi not in fit_windows:
                plt.figure(figsize=(12, 6))
                for ev in datas[chi][:min(len(datas[chi]), 50)]:
                    wf = np.array(ev[1])
                    t = np.arange(len(wf)) * 0.5
                    plt.plot(t, wf, alpha=0.2)
                plt.xlabel("Time [us]")
                plt.ylabel("ADC [bit]")
                plt.title(f"Raw waveforms – CH{chi} ({fname})")
                plt.grid()
                plt.show()

                xmin = float(input(f"[CH{chi}] Fit xmin (us): "))
                xmax = float(input(f"[CH{chi}] Fit xmax (us): "))
                save_master_window(chi, xmin, xmax)
                fit_windows[chi] = (xmin, xmax)
            else:
                xmin, xmax = fit_windows[chi]

            # Perform sinc interpolation fit
            t_fine = np.linspace(xmin, xmax, 2000)
            first_wf = np.array(datas[chi][0][1])
            fixed_ped = float(np.mean(first_wf[0:30]))

            for ev in datas[chi]:
                evt_ts = ev[0] * 10  # conversion ns
                wf = np.array(ev[1]) - fixed_ped
                wf_interp = sinc_interp(np.arange(len(wf)) * 0.5, wf, t_fine, T=0.5)
                idx_min = np.argmin(wf_interp)
                tmin = t_fine[idx_min]
                peak_amp = abs(fixed_ped - (wf_interp[idx_min] + fixed_ped))
                tdszip[chi].append((tmin * 10 + evt_ts, peak_amp))

        append_structured_data(hdf5_fp, tdszip, fname)
        print(f"✅ Saved data from {fname}")

    if new_files_found:
        processed_days += 1
        print(f"✅ Day {date_str} processed.")
    else:
        unprocessed_days += 1
        print(f"📁 Day {date_str} already processed.")

remaining_days = total_days - processed_days - unprocessed_days
print(f"\n✅ Processing complete. {processed_days} new days analyzed, {unprocessed_days} already up-to-date.")
print(f"{remaining_days} days left unprocessed (no .tana files found).")

# ======== If all analyzed, ask whether to redefine fit windows ========
if processed_days == 0 and unprocessed_days == total_days:
    print("\n✅ All .tana files are already processed.")
    ask_refit = input("Re-enter fit windows for all channels? [y/n]: ").strip().lower()
    if ask_refit == 'y':
        print("\n--- Re-defining global fit windows ---")
        with h5py.File(fit_master_fp, 'a') as f:
            for chi in range(32):
                if chi in [0, 16]:
                    continue
                plt.figure(figsize=(12, 6))
                # Load a sample waveform
                for folder in anaata_folders:
                    tana_files = sorted(glob.glob(os.path.join(folder, "*.tana")))
                    if not tana_files:
                        continue
                    with open(tana_files[0], "rb") as fs:
                        datas = pickle.load(fs)
                    if chi >= len(datas) or len(datas[chi]) == 0:
                        continue
                    for ev in datas[chi][:min(len(datas[chi]), 50)]:
                        wf = np.array(ev[1])
                        t = np.arange(len(wf)) * 0.5
                        plt.plot(t, wf, alpha=0.2)
                    break
                plt.xlabel("Time [us]")
                plt.ylabel("ADC [bit]")
                plt.title(f"Re-select fit window – CH{chi}")
                plt.grid()
                plt.show()

                xmin = float(input(f"[CH{chi}] New xmin (us): "))
                xmax = float(input(f"[CH{chi}] New xmax (us): "))
                f["fit_windows"][f"CH{chi:02d}"][:] = [xmin, xmax]
        print("✅ All fit windows updated.")

print("\nAll Anaata folders processed.")
