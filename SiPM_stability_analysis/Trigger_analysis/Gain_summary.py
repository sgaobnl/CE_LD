import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime

# ----------------------------
# Configuration
# ----------------------------
hdf5_output = "/data/disk1/koloina/waveform_fitting/SIPM/LED_Analysis_Final.hdf5"

# Y-axis limits for raw gain by HV group
RAW_GAIN_YLIMS = {
    "HV1": (50, 200),
    "HV2": (50, 300),
    "HV3": (50, 350)
}

# Normalized gain limits (same for all)
NORM_GAIN_YLIM = (0.95, 1.05)

# ----------------------------
# Load and process data
# ----------------------------
def extract_gains(hdf5_path):
    """
    Extract raw and normalized gains from HDF5 file.
    Gain = spacing between 2-PE and 1-PE peaks (fitted_centers[2] - fitted_centers[1]).
    """
    gains_data = {}  # {sipm_id: {'timestamps': [], 'raw_gains': [], 'norm_gains': [], 'hv_group': str}}
    
    with h5py.File(hdf5_path, "r") as f:
        for sipm_id in f.keys():
            # Extract HV group from SiPM ID
            hv_group = "HV3"  # default
            for hv in ["HV1", "HV2", "HV3"]:
                if hv in sipm_id:
                    hv_group = hv
                    break
            
            for femb_key in f[sipm_id].keys():
                femb_group = f[sipm_id][femb_key]
                
                timestamps = []
                raw_gains = []
                
                for date_str in sorted(femb_group.keys()):
                    dset = femb_group[date_str]
                    
                    # Get fitted centers (PE peak positions)
                    if "fitted_centers" not in dset:
                        continue
                    
                    centers = dset["fitted_centers"][:]
                    
                    # Need at least 3 peaks for Gain2 (2-PE minus 1-PE)
                    if len(centers) < 3:
                        continue
                    
                    # Gain2 = difference between 2-PE and 1-PE peaks
                    gain = centers[2] - centers[1]
                    
                    # Filter out low gains (same as your code)
                    if gain < 115:
                        gain = np.nan
                    
                    # Parse timestamp - try both formats
                    try:
                        # Try format with underscores first (from analysis script)
                        dt = datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
                        timestamps.append(dt)
                        raw_gains.append(gain)
                    except Exception:
                        try:
                            # Try format with spaces/colons (alternative)
                            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                            timestamps.append(dt)
                            raw_gains.append(gain)
                        except Exception:
                            print(f"Warning: Could not parse date string: {date_str}")
                            continue
                
                if len(raw_gains) > 0:
                    # Sort by timestamp
                    sorted_indices = np.argsort(timestamps)
                    timestamps = [timestamps[i] for i in sorted_indices]
                    raw_gains = np.array([raw_gains[i] for i in sorted_indices])
                    
                    # Normalize to mean of valid measurements
                    valid_gains = raw_gains[~np.isnan(raw_gains)]
                    if len(valid_gains) == 0:
                        continue
                    
                    mean_gain = np.mean(valid_gains)
                    norm_gains = raw_gains / mean_gain
                    
                    key = f"{sipm_id}/{femb_key}"
                    gains_data[key] = {
                        'timestamps': timestamps,
                        'raw_gains': raw_gains,
                        'norm_gains': norm_gains,
                        'hv_group': hv_group
                    }
    
    return gains_data

# ----------------------------
# Plotting
# ----------------------------
def plot_gains(gains_data):
    """
    Plot raw and normalized gains grouped by HV category.
    Two rows: top = raw gain, bottom = normalized gain.
    """
    # Group by HV
    hv_groups = {"HV1": [], "HV2": [], "HV3": []}
    
    for sipm_key, data in gains_data.items():
        hv_group = data['hv_group']
        if hv_group in hv_groups:
            hv_groups[hv_group].append((sipm_key, data))
    
    # Create subplots: 2 rows x 3 columns
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    
    for col_idx, (hv_name, sipm_list) in enumerate([("HV1", hv_groups["HV1"]), 
                                                      ("HV2", hv_groups["HV2"]), 
                                                      ("HV3", hv_groups["HV3"])]):
        # Top row: Raw gain
        ax_raw = axes[0, col_idx]
        
        for sipm_key, data in sipm_list:
            timestamps = data['timestamps']
            raw_gains = data['raw_gains']
            
            label = sipm_key.split("/")[0][:20]
            ax_raw.plot(timestamps, raw_gains, marker='o', linestyle='-', 
                       markersize=4, alpha=0.7, label=label)
        
        ax_raw.set_ylabel("Raw Gain [ADC]", fontsize=12)
        ax_raw.set_title(f"{hv_name} SiPMs - Raw Gain", fontsize=12, fontweight='bold')
        ax_raw.grid(True, alpha=0.3)
        ax_raw.set_ylim(RAW_GAIN_YLIMS[hv_name])
        ax_raw.tick_params(axis='x', rotation=45)
        
        if len(sipm_list) <= 10:
            ax_raw.legend(fontsize=7, loc='best')
        
        # Bottom row: Normalized gain
        ax_norm = axes[1, col_idx]
        
        for sipm_key, data in sipm_list:
            timestamps = data['timestamps']
            norm_gains = data['norm_gains']
            
            label = sipm_key.split("/")[0][:20]
            ax_norm.plot(timestamps, norm_gains, marker='o', linestyle='-', 
                        markersize=4, alpha=0.7, label=label)
        
        ax_norm.set_xlabel("Date", fontsize=12)
        ax_norm.set_ylabel("Normalized Gain", fontsize=12)
        ax_norm.set_title(f"{hv_name} SiPMs - Normalized", fontsize=12, fontweight='bold')
        ax_norm.grid(True, alpha=0.3)
        ax_norm.set_ylim(NORM_GAIN_YLIM)
        ax_norm.yaxis.set_major_locator(mticker.MultipleLocator(0.05))
        ax_norm.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.5)
        ax_norm.tick_params(axis='x', rotation=45)
        
        if len(sipm_list) <= 10:
            ax_norm.legend(fontsize=7, loc='best')
    
    plt.tight_layout()
    plt.suptitle("SiPM Gain Analysis: Raw and Normalized", fontsize=16, fontweight='bold', y=1.00)
    plt.show()

# ----------------------------
# Main execution
# ----------------------------
if __name__ == "__main__":
    print("Loading gain data from HDF5...")
    print(f"HDF5 path: {hdf5_output}")
    
    # Check if file exists
    import os
    if not os.path.exists(hdf5_output):
        print(f"ERROR: HDF5 file not found at {hdf5_output}")
        exit(1)
    
    # Debug: print file structure
    print("\nDebug: Checking HDF5 structure...")
    with h5py.File(hdf5_output, "r") as f:
        sipm_keys = list(f.keys())
        print(f"Found {len(sipm_keys)} SiPM entries")
        if len(sipm_keys) > 0:
            first_sipm = sipm_keys[0]
            print(f"Example SiPM: {first_sipm}")
            femb_keys = list(f[first_sipm].keys())
            print(f"  FEMBs: {femb_keys}")
            if len(femb_keys) > 0:
                first_femb = femb_keys[0]
                date_keys = list(f[first_sipm][first_femb].keys())
                print(f"  Date entries: {len(date_keys)}")
                if len(date_keys) > 0:
                    print(f"  Example date format: {date_keys[0]}")
                    dset = f[first_sipm][first_femb][date_keys[0]]
                    print(f"  Datasets: {list(dset.keys())}")
                    if "fitted_centers" in dset:
                        centers = dset["fitted_centers"][:]
                        print(f"  fitted_centers length: {len(centers)}")
                        print(f"  fitted_centers values: {centers}")
    
    gains_data = extract_gains(hdf5_output)
    
    print(f"Found {len(gains_data)} SiPM channels with gain data.")
    
    if len(gains_data) == 0:
        print("No gain data found. Check HDF5 file path and contents.")
    else:
        print("Plotting gains...")
        plot_gains(gains_data)
        print("Plot complete.")
