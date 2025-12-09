#!/usr/bin/env python3

import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime
import re

# ----------------------------
# Paths
# ----------------------------
rootdir = "/data/disk1/koloina/waveform_fitting/SIPM/Final_plots/"
hdf5_path = os.path.join(rootdir, "LED_Analysis_Final.hdf5")

output_dir = os.path.join(rootdir, "SNR_plots")
os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Parameters
# ----------------------------
target_hours = [0, 8, 21]

colors = {0: "orange",
          8: "purple",
          21: "blue"}

labels = {0: "00h",
          8: "08h",
          21: "21h"}

# Special channels → use p2/FWHM1
SPECIAL_CHANNELS = {28, 29}

# Layout
MAX_SUBPLOTS = 18
NROWS, NCOLS = 3, 6


# ----------------------------
# Utilities
# ----------------------------
def get_hour_from_datestr(datestr):
    return datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S").hour


def get_day_number(datestr, ref_date):
    dt = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
    return (dt - ref_date).days + 1


def extract_channel_number(channel_name):
    """
    Extract channel number from formats like:
    - HV1_CH28
    - HV2_CH03
    - HV3_..._CH15
    """
    match = re.search(r'CH(\d+)', channel_name)
    if match:
        return int(match.group(1))

    parts = channel_name.split("_")
    for part in reversed(parts):
        nums = re.findall(r'\d+', part)
        if nums:
            return int(nums[-1])

    return -1


# ----------------------------
# Main
# ----------------------------
with h5py.File(hdf5_path, "r") as f:

    channels = list(f.keys())

    # DEBUG printout
    print("\n==== CHANNEL PARSE DEBUG ====")
    for ch in sorted(channels):
        chnum = extract_channel_number(ch)
        flag = " **SPECIAL**" if chnum in SPECIAL_CHANNELS else ""
        print(f"{ch} -> CH{chnum}{flag}")
    print("===============================\n")

    # ----------------------------
    # Group channels by HV prefix
    # ----------------------------
    hv_groups = {}
    for ch in channels:
        prefix = ch.split("_")[0]   # HV1, HV2, HV3...
        hv_groups.setdefault(prefix, []).append(ch)

    # ----------------------------
    # Find earliest date
    # ----------------------------
    all_dates = []
    for ch in channels:
        grp = f[ch]
        for ufemb in grp.keys():
            for date_str in grp[ufemb].keys():
                all_dates.append(
                    datetime.strptime(date_str,
                                      "%Y-%m-%d %H:%M:%S")
                )

    if not all_dates:
        print("No timestamps found.")
        exit(1)

    ref_date = min(all_dates)

# ============================================================
# PLOTTING LOOP
# ============================================================

with h5py.File(hdf5_path, "r") as f:

    for hv, ch_list in hv_groups.items():

        ch_list = sorted(ch_list)[:MAX_SUBPLOTS]

        # ====================================================
        # NORMALIZED SNR FIGURE
        # ====================================================
        fig_norm, axes_norm = plt.subplots(NROWS, NCOLS,
                                            figsize=(20, 10))
        axes_norm = axes_norm.flatten()

        # ====================================================
        # RAW SNR FIGURE
        # ====================================================
        fig_raw, axes_raw = plt.subplots(NROWS, NCOLS,
                                          figsize=(20, 10))
        axes_raw = axes_raw.flatten()

        for i, ch in enumerate(ch_list):

            ax_n = axes_norm[i]
            ax_r = axes_raw[i]

            grp_ch = f[ch]
            ch_num = extract_channel_number(ch)
            is_special = ch_num in SPECIAL_CHANNELS

            snr_data = {h: {} for h in target_hours}
            all_snrs = []

            # ----------------------------
            # SNR CALCULATION
            # ----------------------------
            for ufemb in grp_ch.keys():
                for date_str in grp_ch[ufemb].keys():

                    ds = grp_ch[ufemb][date_str]

                    fitted_centers = ds.get("fitted_centers", None)
                    fwhm = ds.get("fwhms", None)

                    if fitted_centers is None or fwhm is None:
                        continue

                    p = np.array(fitted_centers)
                    w = np.array(fwhm)

                    # --- SNR rules ---
                    if is_special:
                        if len(p) < 3 or len(w) < 2:
                            continue
                        if w[1] == 0 or np.isnan(w[1]) or np.isnan(p[2]):
                            continue
                        snr = p[2] / w[1]
                    else:
                        if len(p) < 2 or len(w) < 1:
                            continue
                        if w[0] == 0 or np.isnan(w[0]) or np.isnan(p[1]):
                            continue
                        snr = p[1] / w[0]

                    # Remove absurd values
                    if snr >= 100:
                        continue

                    day = get_day_number(date_str, ref_date)
                    hour = get_hour_from_datestr(date_str)

                    if hour in target_hours:
                        snr_data[hour][day] = snr
                        all_snrs.append(snr)

            # ----------------------------
            # Handling empty channels
            # ----------------------------
            suffix = " *" if is_special else ""

            if not all_snrs:
                for ax in (ax_n, ax_r):
                    ax.set_title(ch + suffix, fontsize=9)
                    ax.text(0.5, 0.5, "No Data",
                            ha="center", va="center",
                            fontsize=10,
                            color="red")
                    ax.set_axis_off()
                continue

            # ============================
            # NORMALIZATION
            # ============================
            mean_snr = np.nanmean(all_snrs)

            # ============================
            # PLOT BOTH VERSIONS
            # ============================
            for hour in target_hours:

                days = list(snr_data[hour].keys())
                snrs = [snr_data[hour][d] for d in days]
                snrs_norm = [s/mean_snr for s in snrs]

                if not days:
                    continue

                ax_r.scatter(days,
                             snrs,
                             label=labels[hour],
                             color=colors[hour],
                             alpha=0.7,
                             s=20)

                ax_n.scatter(days,
                             snrs_norm,
                             label=labels[hour],
                             color=colors[hour],
                             alpha=0.7,
                             s=20)

            # ----------------------------
            # CONNECTING LINES
            # ----------------------------
            days_union = sorted(
                set().union(
                    *[set(snr_data[h].keys()) for h in target_hours]
                )
            )

            for d in days_union:
                vals = [snr_data[h].get(d)
                        for h in target_hours
                        if d in snr_data[h]]

                if len(vals) != len(target_hours):
                    continue

                # RAW
                ax_r.vlines(d,
                            min(vals),
                            max(vals),
                            colors="grey",
                            alpha=0.4)

                # NORM
                nvals = [v/mean_snr for v in vals]
                ax_n.vlines(d,
                            min(nvals),
                            max(nvals),
                            colors="grey",
                            alpha=0.4)

            # ----------------------------
            # FORMAT AXES
            # ----------------------------
            # RAW
            ax_r.set_title(ch + suffix,
                           fontsize=9,
                           fontweight="bold" if is_special else "normal")

            ymin = max(0, min(all_snrs) * 0.8)
            ymax = max(all_snrs) * 1.2

            ax_r.set_ylim(ymin, ymax)
            ax_r.grid(True, linestyle="--", alpha=0.4)

            # NORMALIZED
            ax_n.set_title(ch + suffix,
                           fontsize=9,
                           fontweight="bold" if is_special else "normal")

            ax_n.set_ylim(0.5, 1.5)
            ax_n.yaxis.set_major_locator(
                mticker.MultipleLocator(0.2))
            ax_n.grid(True, linestyle="--", alpha=0.4)

        # ----------------------------
        # CLEAN UNUSED PANELS
        # ----------------------------
        for j in range(i + 1, len(axes_norm)):
            fig_norm.delaxes(axes_norm[j])
            fig_raw.delaxes(axes_raw[j])

        # ----------------------------
        # GLOBAL NORMALIZED LABELS
        # ----------------------------
        fig_norm.suptitle(
            f"Normalized SNR vs Day — {hv} (* = p2/FWHM1)",
            fontsize=14)

        handles, labs = axes_norm[0].get_legend_handles_labels()
        fig_norm.legend(handles, labs, loc="upper right")

        fig_norm.text(0.5, 0.04, "Day",
                      ha="center", fontsize=12)
        fig_norm.text(0.04, 0.5, "Normalized SNR",
                      va="center", rotation="vertical",
                      fontsize=12)

        fn_norm = os.path.join(output_dir,
                               f"Normalized_SNR_{hv}.png")

        plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
        fig_norm.savefig(fn_norm, bbox_inches="tight")
        plt.close(fig_norm)

        print(f"Saved: {fn_norm}")

        # ----------------------------
        # GLOBAL RAW LABELS
        # ----------------------------
        fig_raw.suptitle(
            f"Raw SNR vs Day — {hv} (* = p2/FWHM1)",
            fontsize=14)

        handles, labs = axes_raw[0].get_legend_handles_labels()
        fig_raw.legend(handles, labs, loc="upper right")

        fig_raw.text(0.5, 0.04, "Day",
                     ha="center", fontsize=12)
        fig_raw.text(0.04, 0.5, "SNR",
                     va="center", rotation="vertical",
                     fontsize=12)

        fn_raw = os.path.join(output_dir,
                              f"Raw_SNR_{hv}.png")

        plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])
        fig_raw.savefig(fn_raw, bbox_inches="tight")
        plt.close(fig_raw)

        print(f"Saved: {fn_raw}")

print("\n✅ All SNR plots produced successfully.")
