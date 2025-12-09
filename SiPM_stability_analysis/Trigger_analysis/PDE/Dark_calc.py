# -*- coding: utf-8 -*-
"""
Compute logarithmic ratios from peak fits:
- ln(first_peak_amp / sum_of_all_peak_amps)
- ln(first_peak_mu / sum_of_all_peak_mus)

Save results to a new HDF5 file: darkrate_peak_ratios.hdf5
"""
import numpy as np
import h5py
import os

# ----------------------------
# Configuration
# ----------------------------
peak_h5_path = "/data/disk1/koloina/CN/SiPM/darkrate_peakfits.hdf5"
output_h5_path = "/data/disk1/koloina/CN/SiPM/darkrate_peak_ratios.hdf5"

# ----------------------------
# Helper functions
# ----------------------------
def ensure_group(parent, name):
    """Create group if it doesn't exist, otherwise return existing."""
    if name in parent:
        return parent[name]
    return parent.create_group(name)

def compute_ratios(amps, mus):
    """
    Compute ln(first_peak / sum_of_all_peaks) for amps and mus.
    Returns (ln_amp_ratio, ln_mu_ratio) or (None, None) if invalid.
    """
    if len(amps) == 0 or len(mus) == 0:
        return None, None
    
    # Get first peak values
    first_amp = amps[0]
    first_mu = mus[0]
    
    # Compute sums
    sum_amps = np.sum(amps)
    sum_mus = np.sum(mus)
    
    # Check for valid ratios (positive values)
    if first_amp <= 0 or sum_amps <= 0 or first_mu <= 0 or sum_mus <= 0:
        return None, None
    
    # Compute logarithmic ratios
    ln_amp_ratio = np.log(first_amp / sum_amps)
    ln_mu_ratio = np.log(first_mu / sum_mus)
    
    return ln_amp_ratio, ln_mu_ratio

# ----------------------------
# Main processing
# ----------------------------
def main():
    if not os.path.isfile(peak_h5_path):
        print(f"Error: {peak_h5_path} does not exist!")
        return
    
    print(f"Reading from: {peak_h5_path}")
    print(f"Writing to: {output_h5_path}")
    
    with h5py.File(peak_h5_path, "r") as fin:
        with h5py.File(output_h5_path, "w") as fout:
            
            # Iterate through SiPM groups
            for sipm_name in fin.keys():
                print(f"\nProcessing SiPM: {sipm_name}")
                sipm_group_in = fin[sipm_name]
                sipm_group_out = ensure_group(fout, sipm_name)
                
                # Iterate through uFEMB groups
                for femb_name in sipm_group_in.keys():
                    print(f"  {femb_name}")
                    femb_group_in = sipm_group_in[femb_name]
                    femb_group_out = ensure_group(sipm_group_out, femb_name)
                    
                    # Iterate through hour groups
                    for hour_name in femb_group_in.keys():
                        hour_group_in = femb_group_in[hour_name]
                        
                        # Read amp and mu datasets
                        if "amp" not in hour_group_in or "mu" not in hour_group_in:
                            print(f"    Skipping {hour_name}: missing amp or mu data")
                            continue
                        
                        amps = hour_group_in["amp"][:]
                        mus = hour_group_in["mu"][:]
                        timestamps = hour_group_in["timestamp"][:] if "timestamp" in hour_group_in else None
                        
                        if len(amps) == 0 or len(mus) == 0:
                            print(f"    Skipping {hour_name}: no data")
                            continue
                        
                        # Compute ratios
                        ln_amp_ratio, ln_mu_ratio = compute_ratios(amps, mus)
                        
                        if ln_amp_ratio is None or ln_mu_ratio is None:
                            print(f"    Skipping {hour_name}: invalid ratio (negative or zero values)")
                            continue
                        
                        # Save to output file
                        hour_group_out = ensure_group(femb_group_out, hour_name)
                        hour_group_out.create_dataset("ln_amp_ratio", data=ln_amp_ratio)
                        hour_group_out.create_dataset("ln_mu_ratio", data=ln_mu_ratio)
                        hour_group_out.create_dataset("num_peaks", data=len(amps))
                        
                        # Also save first timestamp if available
                        if timestamps is not None and len(timestamps) > 0:
                            hour_group_out.create_dataset("timestamp", data=timestamps[0])
                        
                        print(f"    {hour_name}: ln_amp_ratio={ln_amp_ratio:.4f}, ln_mu_ratio={ln_mu_ratio:.4f}, num_peaks={len(amps)}")
    
    print(f"\nProcessing complete! Results saved to: {output_h5_path}")

if __name__ == "__main__":
    main()
