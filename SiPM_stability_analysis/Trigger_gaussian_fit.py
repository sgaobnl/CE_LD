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
                tmps = line.split(",")
                chno = int(tmps[6])
                if len(tmps[12]) >= 0:
                    sipmno = tmps[12][0:3] + "_" + tmps[9] + "_" + tmps[11] + "_" + "CH%02d" % chno + "_FNL" + tmps[4]
                    dmap[chno] = sipmno
else:
    print("%s doesn't exist" % fm)
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
califp = rootdir + "led_cali_vs_time_30.hdf5"

# Global dict to collect envelope fits
daily_envelopes = dict()

for root, dirs, files in os.walk(rootdir):
    break

rstdirs = [onedir for onedir in dirs if "Result_" in onedir]

for subdir in rstdirs:
    rst_dir = rootdir + subdir + "/"
    print(rst_dir)

    for ufemb_id in [1]:
        hdf5_fp = rst_dir + "uFEMB%d_%s_trigger.hdf5" % (ufemb_id, subdir[7:15])

        if not os.path.isfile(hdf5_fp):
            print(hdf5_fp)
            continue

        with h5py.File(hdf5_fp, "r") as f:
            fns = f["file_analyzed"][:]
            if len(fns) == 0:
                continue
            fns.sort()
            fn0 = fns[0].decode('utf-8')
            ts0 = int(fn0[fn0.find(".tana") - 32:fn0.find(".tana")])
            dt0 = datetime.strptime(fn0[7:7+14], "%Y%m%d_%H_%M").replace(tzinfo=ZoneInfo("America/New_York"))
            dtt0 = int(dt0.timestamp())

            for ch in range(32):
                key = "CH%02d" % ch
                dn = dmap[(ufemb_id - 1) * 32 + ch]
                if "OPEN" in dn:
                    print(dn, "is ignored")
                    continue
                print(dn, "is being analyzed")

                plt_dir = rst_dir + dn + "_plots/Triggers/"
                os.makedirs(plt_dir, exist_ok=True)

                for root, dirs, files in os.walk(plt_dir):
                    break
                pltfiles = sorted([tmp for tmp in files if ".png" in tmp])[:-1]

                data = f[key][:]
                if len(data) > 0:
                    ts, ds = zip(*data)
                    ts = np.array(ts) - ts0 * 10
                    ds = np.array(ds)
                    diffs = ts[1:] - ts[:-1]
                    jumps = np.where(diffs > 1e9)[0]

                    subts, subds = [], []
                    prev = 0
                    for idx in jumps:
                        subt, subd = ts[prev:idx+1].copy(), ds[prev:idx+1].copy()
                        poss = np.where(subd > 30)[0]
                        if len(poss) < 10:
                            prev = idx + 1
                            continue
                        posb, pose = poss[0], poss[-1]
                        subts.append(subt[posb:pose])
                        subds.append(subd[posb:pose])
                        prev = idx + 1
                    subts.append(ts[prev:].copy())
                    subds.append(ds[prev:].copy())

                    resolutions = []
                    resolution_times = []

                    for xi in range(len(subts)):
                        dtt00 = dtt0 + int(subts[xi][0] // 1e9)
                        dt = datetime.fromtimestamp(dtt00, tz=pytz.timezone("America/New_York"))
                        pltexist = dt.strftime("%Y_%m_%d_%H_%M_%S")
                        pltexist_f = any(pltexist in pltfile for pltfile in pltfiles)
                        if pltexist_f:
                            continue

                        vbinw = 1
                        counts, bin_edges = np.histogram(subds[xi],
                                                         bins=range(min(subds[xi]), max(subds[xi]) + vbinw, vbinw))
                        peaks, properties = find_peaks(counts, prominence=20, distance=30)
                        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
                        peak_centers = bin_centers[peaks]
                        peak_heights = counts[peaks]

                        fitted_centers = []
                        fitted_sigmas = []
                        fitted_amplitudes = []
                        gauss_params = []

                        for peak_idx in peaks[1:]:  # skip first peak
                            center = bin_centers[peak_idx]
                            window = (bin_centers > center - 15) & (bin_centers < center + 15)
                            x_fit, y_fit = bin_centers[window], counts[window]
                            if len(x_fit) < 5:
                                continue
                            try:
                                sigma_guess = (x_fit[-1] - x_fit[0]) / 6
                                p0 = [np.max(y_fit), center, sigma_guess]
                                popt, _ = curve_fit(gaussian, x_fit, y_fit, p0=p0)
                                gauss_params.append(popt)
                                fitted_amplitudes.append(popt[0])
                                fitted_centers.append(popt[1])
                                fitted_sigmas.append(popt[2])
                            except Exception as e:
                                print(f"Could not fit Gaussian at {center:.1f}: {e}")

                        fwhms = [2.355 * s for s in fitted_sigmas]
                        res_values = []
                        for i in range(len(fitted_centers) - 1):
                            delta = fitted_centers[i + 1] - fitted_centers[i]
                            res = delta / fwhms[i] if fwhms[i] > 0 else np.nan
                            res_values.append(res)
                            print(f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] ΔP = {delta:.2f}, FWHM = {fwhms[i]:.2f}, Resolution = {res:.3f}")

                        if len(res_values) > 0:
                            avg_res = np.nanmean(res_values)
                            resolutions.append(avg_res)
                            resolution_times.append(dt)

                        fig, axes = plt.subplots(3, 1, figsize=(8, 14))
                        fig.suptitle(dn + " starting at {}".format(dt.strftime("%Y-%m-%d %H:%M:%S")))

                        axes[0].scatter((np.array(subts[xi]) - subts[xi][0]) / 1e9, subds[xi],
                                        color='green', marker='.')
                        axes[0].set_title('SiPM Output')
                        axes[0].set_xlabel('Time / s')
                        axes[0].set_ylabel('Amplitude Peak / ADC bit')
                        axes[0].set_ylim((0, 2000))
                        axes[0].grid()

                        axes[1].hist(subds[xi],
                                     bins=range(min(subds[xi]), max(subds[xi]) + vbinw, vbinw),
                                     color='blue', edgecolor='black')
                        x_smooth = np.linspace(min(bin_centers), max(bin_centers), 1000)
                        for A, mu, sigma in gauss_params:
                            y_gauss = gaussian(x_smooth, A, mu, sigma)
                            axes[1].plot(x_smooth, y_gauss, 'r--')
                            axes[1].annotate(f'{mu:.1f}', xy=(mu, A), xytext=(0, 8),
                                             textcoords='offset points', ha='center', color='red')

                        axes[1].set_title('Amplitude distribution')
                        axes[1].set_xlabel('Amplitude / ADC bit')
                        axes[1].set_ylabel('Counts')
                        axes[1].grid()

                        axes[2].plot(fitted_centers, fitted_amplitudes, 'ro', label='Gaussian Peak Centers')
                        axes[2].set_xlim(axes[1].get_xlim())  # match axis
                        axes[2].set_ylim(axes[1].get_ylim())
                        if len(fitted_centers) >= 3:
                            try:
                                def peak_envelope(x, A, mu, sigma):
                                    return gaussian(x, A, mu, sigma)

                                p0_env = [max(fitted_amplitudes), np.mean(fitted_centers), np.std(fitted_centers)]
                                popt_env, _ = curve_fit(peak_envelope, fitted_centers, fitted_amplitudes, p0=p0_env)
                                x_line = np.linspace(min(fitted_centers), max(fitted_centers), 500)
                                y_line = peak_envelope(x_line, *popt_env)
                                axes[2].plot(x_line, y_line, 'k--', label='Gaussian Fit to Peaks')

                                mu_env, sigma_env = popt_env[1], popt_env[2]
                                fwhm_env = 2.355 * sigma_env
                                print(f"Envelope Fit → μ={mu_env:.2f}, σ={sigma_env:.2f}, FWHM={fwhm_env:.2f}")

                                output_dir = os.path.join(rst_dir, dn + "_plots/FitParams")
                                os.makedirs(output_dir, exist_ok=True)
                                outfp = os.path.join(output_dir, "fwhm_log.txt")
                                with open(outfp, "a") as outf:
                                    outf.write(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}, {mu_env:.2f}, {sigma_env:.2f}, {fwhm_env:.2f}\n")

                                # -----------------------------
                                # SAVE ENVELOPE FIT FOR LATER OVERLAY
                                # -----------------------------
                                if dn.startswith("HV1") or dn.startswith("HV2"):
                                    date_str = dt.strftime("%Y-%m-%d")
                                    if dn not in daily_envelopes:
                                        daily_envelopes[dn] = dict()
                                    if date_str not in daily_envelopes[dn]:
                                        daily_envelopes[dn][date_str] = []
                                    daily_envelopes[dn][date_str].append((x_line, y_line))

                            except Exception as e:
                                print("Global Gaussian fit failed:", e)

                        axes[2].set_title('Envelope Fit')
                        axes[2].set_xlabel('Amplitude / ADC bit')
                        axes[2].set_ylabel('Counts')
                        axes[2].legend()
                        axes[2].grid()

                        plt.tight_layout()
                        pltfp = os.path.join(plt_dir,
                                             "Trig_%s_%s.png" % (dn, dt.strftime("%Y_%m_%d_%H_%M_%S")))
                        fig.savefig(pltfp, format='png')
                        print(f"Plot saved to {pltfp}")
                        plt.close()

# ----------------------------
# Plot overlays per day
# ----------------------------

for dn, day_dict in daily_envelopes.items():
    for date_str, env_list in sorted(day_dict.items()):
        fig, ax = plt.subplots(figsize=(10, 6))
        for idx, (xenv, yenv) in enumerate(env_list):
            ax.plot(xenv, yenv, label=f"Trigger {idx+1}", lw=1.5)
        ax.set_title(f"{dn} - Envelope Fits on {date_str}")
        ax.set_xlabel("Amplitude (ADC bits)")
        ax.set_ylabel("Counts")
        ax.legend(fontsize='small')
        ax.grid()

        output_dir = os.path.join(rootdir, f"{dn}_overlays")
        os.makedirs(output_dir, exist_ok=True)
        outfp = os.path.join(output_dir, f"{date_str}.png")
        fig.savefig(outfp, dpi=300)
        plt.close(fig)
        print(f"Overlay plot saved → {outfp}")
