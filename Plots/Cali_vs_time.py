import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

file_path = 'femb2_led_cali_vs_time.hdf5' #add your file path
output_dir = 'plots_cali_vs_time_femb2'   #add any output directory to store the plots (optional)

def parse_datetime(name):
    return datetime.strptime(name, "%Y_%m_%d_%H_%M_%S")

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

with h5py.File(file_path, 'r') as f:
    # Loop over all groups in the root of the file
    for group_name in f.keys():
        group = f[group_name]
        dataset_names = sorted(group.keys(), key=parse_datetime)
        
        if len(dataset_names) == 0:
            print(f"No datasets in group {group_name}, skipping.")
            continue
        
        # Use first dataset as T0 for this group
        T0 = parse_datetime(dataset_names[0])
        
        plt.figure(figsize=(10,6))
        
        for dataset_name in dataset_names:
            current_time = parse_datetime(dataset_name)
            delta_hours = (current_time - T0).total_seconds() / 3600.0
            
            dataset = group[dataset_name]
            data = dataset[()]
            
            if 'PeakADC' in data.dtype.names:
                peak_adc = data['PeakADC']
                if len(peak_adc) < 2:
                    continue
                
                delta_peak_adc = np.diff(peak_adc)
                x_vals = np.full_like(delta_peak_adc, delta_hours, dtype=float)
                
                #plt.plot(x_vals, delta_peak_adc, 'o', label=f"T={delta_hours:.1f} h") to set legends (optional)
                plt.plot(x_vals, delta_peak_adc, 'o')
        
        plt.xlabel("Time (hours)")
        plt.ylabel("Gain")
        plt.title(f"Gain vs time for Group: {group_name}")
        plt.grid(True)
        plt.tight_layout()
        #plt.legend(fontsize='small', loc='upper right') to see legends
        
        # Save the figure
        save_path = os.path.join(output_dir, f"{group_name}cali_vs_time.png")
        plt.savefig(save_path)
        plt.close()
        print(f"Saved plot for group {group_name} to {save_path}")
