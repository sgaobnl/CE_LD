import h5py
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.signal import find_peaks
from datetime import datetime, timedelta

# -----------------------------
# Date range filter
# -----------------------------
START_DATE = datetime(2025, 5, 5)
END_DATE   = datetime(2025, 8, 22, 23, 59, 59)

def parse_dataset_date(name):
    """Parse dataset name like '2025_05_07_13' into datetime."""
    try:
        return datetime.strptime(name, "%Y_%m_%d_%H")
    except Exception:
        return None

def dataset_in_range(name):
    dt = parse_dataset_date(name)
    if dt is None:
        return False
    return START_DATE <= dt <= END_DATE

# -----------------------------
# Combine datasets from group1/group2
# -----------------------------
def get_avg_values(group1, group2):
    """Return (timestamps, avg_values) within date range."""
    avg_values = []
    timestamps = []
    datasets_1 = set(group1.keys()) if group1 else set()
    datasets_2 = set(group2.keys()) if group2 else set()
    all_datasets = sorted(datasets_1 | datasets_2)

    for dataset_name in all_datasets:
        if not dataset_in_range(dataset_name):
            continue

        dataset = None
        if group1 and dataset_name in group1:
            dataset = group1[dataset_name]
        elif group2 and dataset_name in group2:
            dataset = group2[dataset_name]

        if dataset and isinstance(dataset, h5py.Dataset) and 'Avg(<20Hz)' in dataset.attrs:
            avg_20hz = dataset.attrs['Avg(<20Hz)']
            dt = parse_dataset_date(dataset_name)
            if dt:
                avg_values.append(avg_20hz)
                timestamps.append(dt)

    return np.array(timestamps), np.array(avg_values, dtype=float)

# -----------------------------
# Histogram plotting with peak detection (only highest peak)
# -----------------------------
def plot_histograms_subplots(hv_prefix, groups, h5f1, h5f2, output_dir='plots_combined_femb1_femb2_filtered'):
    fig, axs = plt.subplots(6, 3, figsize=(18, 12), sharex=True, sharey=True)
    axs = axs.flatten()
    std_dict = {}
    peak_dict = {}

    for i, group_name in enumerate(groups):
        if i >= 18:
            break

        group1 = h5f1[group_name] if group_name in h5f1 else None
        group2 = h5f2[group_name] if group_name in h5f2 else None

        ts, avg_values = get_avg_values(group1, group2)
        if avg_values.size == 0:
            print(f"No valid Avg(<20Hz) in {group_name} (date filtered). Skipping histogram subplot.")
            continue

        values = np.array(avg_values, dtype=float)
        std_val = np.nanstd(values)
        std_dict[group_name] = std_val

        hist, bin_edges = np.histogram(values[~np.isnan(values)], bins=100)
        centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        peaks_indices, _ = find_peaks(hist, height=np.max(hist)*0.1)
        if len(peaks_indices) > 0:
            highest_peak_idx = peaks_indices[np.argmax(hist[peaks_indices])]
            peak_centers = np.array([centers[highest_peak_idx]])
        else:
            peak_centers = np.array([])

        peak_dict[group_name] = peak_centers.tolist()

        axs[i].bar(centers, hist, width=bin_edges[1]-bin_edges[0], color='blue', edgecolor='black')
        for peak_center in peak_centers:
            peak_height = hist[np.abs(centers - peak_center).argmin()]
            axs[i].bar(peak_center, peak_height, width=bin_edges[1]-bin_edges[0], color='red', edgecolor='black')
            axs[i].text(peak_center, peak_height + max(hist)*0.05, f"{peak_center:.2f}",
                        color='red', fontsize=7, ha='center', va='bottom')

        axs[i].set_title(f"{group_name}\nstd={std_val:.3f}", fontsize=8)
        axs[i].set_xlim(0, 3)
        axs[i].grid(True)
        axs[i].tick_params(axis='both', which='major', labelsize=7)

    fig.suptitle(f"Histograms of Avg(<20Hz) for {hv_prefix} groups (May 5 – Aug 22)", fontsize=16)
    fig.text(0.5, 0.04, 'Avg(<20Hz) Value', ha='center', fontsize=14)
    fig.text(0.04, 0.5, 'Count', va='center', rotation='vertical', fontsize=14)
    plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f'Histograms_{hv_prefix}_Avg_20Hz.png')
    plt.savefig(filepath)
    plt.show()
    plt.close()
    print(f"Saved histogram subplots figure for {hv_prefix} as '{filepath}'")

    return std_dict, peak_dict

# -----------------------------
# Plot normalized data subplots for all HV groups
# -----------------------------
def plot_normalized_subplots(hv_prefix, groups, filtered_data_dict, original_data_dict,
                             output_dir='plots_combined_femb1_femb2_filtered',
                             ylims=(0, 2)):
    fig, axs = plt.subplots(6, 3, figsize=(18, 12), sharex=True, sharey=True)
    axs = axs.flatten()

    total_days = (END_DATE.date() - START_DATE.date()).days + 1  # inclusive
    day_numbers = np.arange(total_days)

    for i, group_name in enumerate(groups):
        if i >= 18:
            break

        if hv_prefix == 'HV1':
            ts, data = filtered_data_dict.get(group_name, ([], []))
            if len(data) == 0:
                continue
        else:
            ts, data = original_data_dict.get(group_name, ([], []))
            if len(data) == 0:
                continue

        # Allocate full [days * 24] with NaNs
        full_hours = np.full(total_days * 24, np.nan)

        for t, val in zip(ts, data):
            if START_DATE <= t <= END_DATE:
                hour_index = int((t - START_DATE).total_seconds() // 3600)
                if 0 <= hour_index < len(full_hours):
                    full_hours[hour_index] = val

        # Reshape into days × 24
        full_hours = full_hours.reshape(total_days, 24)

        # Normalize
        global_mean = np.nanmean(full_hours)
        if np.isnan(global_mean) or global_mean == 0:
            continue
        normalized = full_hours / global_mean

        # Per-day mean & std
        normalized_per_day_mean = np.nanmean(normalized, axis=1)
        normalized_per_day_std = np.nanstd(normalized, axis=1)

        ax = axs[i]
        ax.errorbar(day_numbers, normalized_per_day_mean, yerr=normalized_per_day_std,
                    fmt='o-', markersize=1, capsize=3)
        ax.set_ylim(*ylims)
        ax.set_title(group_name, fontsize=8)
        ax.grid(True)
        ax.tick_params(axis='both', which='major', labelsize=7)
        ax.axhline(1, color='red', linestyle='--', linewidth=2)
        # -----------------------------
        # Annotate the start point for HV1 on the x-axis with day number
        # -----------------------------
        if hv_prefix == 'HV1':
            valid_indices = np.where(~np.isnan(normalized_per_day_mean))[0]
            if valid_indices.size > 0:
                first_idx = valid_indices[0]
                start_x = day_numbers[first_idx]

                ax.text(start_x, ax.get_ylim()[0] - 0.02,  # just below x-axis
                        str(start_x),                      # only the number
                        fontsize=7, color="green", ha="center", va="top")

    fig.suptitle(f'Normalized DCR per Day with Std Dev for {hv_prefix}', fontsize=16)
    fig.text(0.5, 0.04, 'Day Number', ha='center', fontsize=14)
    fig.text(0.04, 0.5, 'Normalized DCR', va='center', rotation='vertical', fontsize=14)
    plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

    filepath = os.path.join(output_dir, f'Normalized_DCR_per_day_{hv_prefix}_subplots.png')
    plt.savefig(filepath)
    plt.show()
    plt.close()
    print(f"Saved normalized DCR subplot figure for {hv_prefix} as '{filepath}'")

# -----------------------------
# Save filtered HV1 data to HDF5
# -----------------------------
def save_filtered_hv1(filtered_data_dict, filename='filtered_HV1_output.h5'):
    with h5py.File(filename, 'w') as hf:
        for group_name, (ts, data) in filtered_data_dict.items():
            grp = hf.create_group(group_name)
            grp.create_dataset("timestamps", data=[t.strftime("%Y-%m-%d %H:%M:%S") for t in ts])
            grp.create_dataset("after_572h_avg", data=data)
    print(f"Filtered HV1 data saved to: {filename}")

# -----------------------------
# Main logic
# -----------------------------
def run_all():
    filename1 = '/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/new data/ufemb1/darkrate_vs_time.hdf5'
    filename2 = '/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/new data/ufemb1/ufemb2/darkrate_vs_time.hdf5'
    output_dir = '/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/new data/plots_combined_femb1_femb2_filtered'
    os.makedirs(output_dir, exist_ok=True)

    ylim_dict = {
        'HV1': (0, 3),
        'HV2': (0, 4),
        'HV3': (-5, 10),
    }
    ylim_normalized_dict = {
        'HV1': (0.88, 1.12),
        'HV2': (0.88, 1.12),
        'HV3': (0.88, 1.12),
    }

    with h5py.File(filename1, 'r') as f1, h5py.File(filename2, 'r') as f2:
        hv_groups = {'HV1': [], 'HV2': [], 'HV3': []}
        all_group_names = set(f1.keys()) | set(f2.keys())

        for group_name in sorted(all_group_names):
            if group_name.startswith('HV1'):
                hv_groups['HV1'].append(group_name)
            elif group_name.startswith('HV2'):
                hv_groups['HV2'].append(group_name)
            elif group_name.startswith('HV3'):
                hv_groups['HV3'].append(group_name)

        filtered_data_dict = {}
        original_data_dict = {}

        for hv_prefix, groups in hv_groups.items():
            if not groups:
                print(f"No groups found for {hv_prefix}. Skipping.")
                continue

            plot_histograms_subplots(hv_prefix, groups, f1, f2, output_dir=output_dir)

            if hv_prefix == 'HV1':
                for group_name in groups[:18]:
                    group1 = f1.get(group_name)
                    group2 = f2.get(group_name)
                    ts, avg_values = get_avg_values(group1, group2)
                    if len(avg_values) > 572:
                        ts = ts[572:]
                        avg_values = avg_values[572:]
                        filtered_data_dict[group_name] = (ts, avg_values)

                save_filtered_hv1(filtered_data_dict)

                plot_normalized_subplots(hv_prefix, groups[:18], filtered_data_dict, None,
                                        output_dir=output_dir,
                                        ylims=ylim_normalized_dict.get(hv_prefix, (0, 2)))

            else:
                for group_name in groups[:18]:
                    group1 = f1.get(group_name)
                    group2 = f2.get(group_name)
                    ts, avg_values = get_avg_values(group1, group2)
                    original_data_dict[group_name] = (ts, avg_values)

                plot_normalized_subplots(hv_prefix, groups[:18], None, original_data_dict,
                                        output_dir=output_dir,
                                        ylims=ylim_normalized_dict.get(hv_prefix, (0, 2)))


if __name__ == "__main__":
    run_all()

