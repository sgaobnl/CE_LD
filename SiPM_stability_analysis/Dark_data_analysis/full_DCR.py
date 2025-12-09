import h5py
import matplotlib.pyplot as plt
import os
import numpy as np

def get_avg_values(group1, group2):
    """
    Combine datasets from group1 and group2
    Return list of Avg(<20Hz) from all datasets
    """
    avg_values = []
    datasets_1 = set(group1.keys()) if group1 else set()
    datasets_2 = set(group2.keys()) if group2 else set()
    all_datasets = sorted(datasets_1 | datasets_2)  # sorted for consistent order

    for dataset_name in all_datasets:
        dataset = None
        if group1 and dataset_name in group1:
            dataset = group1[dataset_name]
        elif group2 and dataset_name in group2:
            dataset = group2[dataset_name]

        if dataset and isinstance(dataset, h5py.Dataset) and 'Avg(<20Hz)' in dataset.attrs:
            avg_20hz = dataset.attrs['Avg(<20Hz)']
            avg_values.append(avg_20hz)

    return avg_values

def main():
    filename1 = '/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/new data/uFEMB1_darkrate_vs_time.hdf5'
    filename2 = '/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/new data/uFEMB2_darkrate_vs_time.hdf5'
    output_dir = '/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/new data/plots_combined_femb1_femb2_subplots'

    os.makedirs(output_dir, exist_ok=True)

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

        for hv_prefix, groups in hv_groups.items():
            if not groups:
                print(f"No groups found for {hv_prefix}. Skipping.")
                continue

            # --- Plot 1: Avg(<20Hz) vs hours ---
            fig, axs = plt.subplots(6, 3, figsize=(18, 12), sharex=True, sharey=True)
            axs = axs.flatten()

            for i, group_name in enumerate(groups):
                if i >= 18:
                    print(f"More than 18 groups in {hv_prefix}, skipping extras.")
                    break

                group1 = f1[group_name] if group_name in f1 else None
                group2 = f2[group_name] if group_name in f2 else None

                avg_values = get_avg_values(group1, group2)

                if not avg_values:
                    print(f"No valid 'Avg(<20Hz)' found for group {group_name}. Skipping subplot.")
                    continue

                num_hours = len(avg_values)
                time_hours = list(range(num_hours))

                ax = axs[i]
                ax.plot(time_hours, avg_values, marker='o', markersize=1, linestyle='-')
                ax.set_ylim(-3,3)
                ax.set_title(group_name, fontsize=8)
                ax.grid(True)
                ax.tick_params(axis='both', which='major', labelsize=7)

            fig.suptitle(f'Avg(<20Hz) vs Duration (hours) for {hv_prefix} (merged femb1 & femb2)', fontsize=16)
            fig.text(0.5, 0.04, 'Duration (hours)', ha='center', fontsize=14)
            fig.text(0.04, 0.5, 'Avg(<20Hz)', va='center', rotation='vertical', fontsize=14)

            plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])
            filepath = os.path.join(output_dir, f'Avg_20Hz_{hv_prefix}_merged_subplots.png')
            plt.savefig(filepath)
            plt.close()
            print(f"Saved merged subplot figure for {hv_prefix} as '{filepath}'")

            # --- Plot 2: Normalized DCR per day with std ---
            fig2, axs2 = plt.subplots(6, 3, figsize=(18, 12), sharex=True, sharey=True)
            axs2 = axs2.flatten()

            for i, group_name in enumerate(groups):
                if i >= 18:
                    break

                group1 = f1[group_name] if group_name in f1 else None
                group2 = f2[group_name] if group_name in f2 else None

                avg_values = get_avg_values(group1, group2)

                if not avg_values:
                    continue

                avg_values = np.array(avg_values)
                num_hours = len(avg_values)

                num_days = num_hours // 24
                if num_days == 0:
                    continue

                global_mean = np.mean(avg_values)

                normalized_dcr_all_hours = avg_values/ global_mean
                normalized_dcr_all_hours = normalized_dcr_all_hours[:num_days*24].reshape(num_days, 24)

                normalized_dcr_per_day_mean = normalized_dcr_all_hours.mean(axis=1)
                normalized_dcr_per_day_std = normalized_dcr_all_hours.std(axis=1)

                day_numbers = np.arange(num_days)

                ax2 = axs2[i]
                ax2.errorbar(day_numbers, normalized_dcr_per_day_mean, yerr=normalized_dcr_per_day_std,
                             fmt='o-', markersize=1, capsize=3)
                ax2.set_ylim(-1,2)
                ax2.set_title(group_name, fontsize=8)
                ax2.grid(True)
                ax2.tick_params(axis='both', which='major', labelsize=7)

            fig2.suptitle(f'Normalized DCR per Day with Std Dev for {hv_prefix} (merged femb1 & femb2)', fontsize=16)
            fig2.text(0.5, 0.04, 'Day Number', ha='center', fontsize=14)
            fig2.text(0.04, 0.5, 'Normalized DCR', va='center', rotation='vertical', fontsize=14)

            plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])
            filepath2 = os.path.join(output_dir, f'Normalized_DCR_per_day_with_std_{hv_prefix}_merged_subplots.png')
            plt.savefig(filepath2)
            plt.close()
            print(f"Saved normalized DCR per day subplot figure with std for {hv_prefix} as '{filepath2}'")

if __name__ == "__main__":
    main()
