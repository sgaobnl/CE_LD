import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

file_path = 'femb1_led_cali_vs_time.hdf5'
output_dir = 'plots_cali_vs_time_femb1'
log_file = os.path.join(output_dir, 'gain_selection_log.txt')

def parse_datetime(name):
    return datetime.strptime(name, "%Y_%m_%d_%H_%M_%S")

os.makedirs(output_dir, exist_ok=True)

gain_styles = [
    {'marker': 'o', 'color': 'blue',  'label': 'Gain 1'},
    {'marker': '+', 'color': 'green', 'label': 'Gain 2'},
    {'marker': '^', 'color': 'red',   'label': 'Gain 3'},
]

with open(log_file, 'w') as log:
    with h5py.File(file_path, 'r') as f:
        for group_name in f.keys():
            if not isinstance(f[group_name], h5py.Group):
                continue

            group = f[group_name]
            dataset_names = sorted(group.keys(), key=parse_datetime)

            if not dataset_names:
                print(f"No datasets in group {group_name}, skipping.", file=log)
                continue

            T0 = parse_datetime(dataset_names[0])
            plt.figure(figsize=(10, 6))
            plotted_labels = [False, False, False]

            for dataset_name in dataset_names:
                current_time = parse_datetime(dataset_name)
                delta_hours = (current_time - T0).total_seconds() / 3600.0

                data = group[dataset_name][()]

                if 'PeakADC' in data.dtype.names and 'PeakCNT' in data.dtype.names:
                    peak_adc = data['PeakADC']
                    peak_cnt = data['PeakCNT']

                    mask = peak_cnt > 500
                    filtered_adc = peak_adc[mask]

                    print(f"\nGroup: {group_name} | Dataset: {dataset_name} | Time: {delta_hours:.2f} h", file=log)
                    print("Filtered PeakADC (PeakCNT > 500):", filtered_adc, file=log)

                    if len(filtered_adc) >= 5:
                        gain = np.diff(filtered_adc)
                        selected_gains = gain[1:4]  # skip first diff

                        print("All ΔPeakADC:", gain, file=log)

                        for i, g in enumerate(selected_gains):
                            if g >= 100:
                                style = gain_styles[i]
                                label = style['label'] if not plotted_labels[i] else None
                                plt.plot(delta_hours, g, style['marker'], color=style['color'], label=label)
                                plotted_labels[i] = True
                                print(f"Gain {i+1}: {g} (used)", file=log)
                            else:
                                print(f"Gain {i+1}: {g} (dropped, < 100)", file=log)
                    else:
                        print("Not enough PeakADC values for gain selection.", file=log)

            plt.xlabel("Time (hours)")
            plt.ylabel("Gain (ΔPeakADC)")
            plt.title(f"Gains ≥ 100 vs Time for Group: {group_name}")
            plt.grid(True)
            plt.tight_layout()
            plt.legend(loc='upper right', fontsize='small')

            save_path = os.path.join(output_dir, f"{group_name}_gain_vs_time.png")
            plt.savefig(save_path)
            plt.close()
            print(f"Saved plot for {group_name} to {save_path}", file=log)
