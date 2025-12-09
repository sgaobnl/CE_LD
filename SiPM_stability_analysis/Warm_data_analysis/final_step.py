# -*- coding: utf-8 -*-
"""
Gaussian Fit Analysis for SiPM Channels
Generates 3x6 subplot grids with Gaussian fits for histogram peaks
Saves histogram data + Gaussian peak info in TXT files
Saves the plots as PNG files
"""

import numpy as np
import h5py
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

# Gaussian function for fitting
def gaussian(x, amplitude, mean, sigma):
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * sigma ** 2))

# Load channel mapping
fm = """/data/disk1/koloina/raw_data/chn_mapping.csv"""
dmap = {}
if os.path.isfile(fm):    
    with open(fm, "r") as f:
        for line in f:
            if "femb" in line:
                continue
            tmps = line.strip().split(",")
            chno = int(tmps[6])
            if len(tmps[12]) >= 0:
                sipmno = tmps[12][0:3] + "_" + tmps[9] + "_" + tmps[11] + "_" + "CH%02d" % chno + "_FNL" + tmps[4] 
                dmap[chno] = sipmno
else:
    print(f"{fm} doesn't exist")
    exit()    

rootdir = """/data/disk1/koloina/raw_data/"""

# Find result directories
for root, dirs, files in os.walk(rootdir):
    break

rstdirs = [d for d in dirs if "Result_" in d]

# Process each result directory
for subdir in rstdirs:
    rst_dir = os.path.join(rootdir, subdir)
    print(f"Processing: {rst_dir}")
    
    ufemb_id = 1  # HV1
    hdf5_fp = os.path.join(rst_dir, f"uFEMB{ufemb_id}_{subdir[7:15]}_trigger.hdf5")
    
    if not os.path.isfile(hdf5_fp):    
        print(f"{hdf5_fp} not found, skipping...")
        continue
    
    folder_timestamp = subdir[7:]  # e.g., "20241204_14"
    
    channel_data = {}
    
    # Load HDF5 data
    with h5py.File(hdf5_fp, "r") as f:
        fns = f["file_analyzed"][:]
        if len(fns) == 0:
            continue
        
        fns.sort()
        fn0 = fns[0].decode('utf-8')
        postana = fn0.find(".tana")
        ts0 = int(fn0[postana-32:postana])
        
        # Collect channel data
        for ch in range(32):
            key = f"CH{ch:02d}"
            dn = dmap.get((ufemb_id - 1) * 32 + ch, f"CH{ch:02d}_UNKNOWN")
            
            if "OPEN" in dn:
                continue
            
            data = f[key][:]
            if len(data) == 0:
                continue
            
            ts, ds = zip(*data)
            ds = np.array(ds)
            channel_data[ch] = {'dn': dn, 'data': ds}
    
    # Plot 3x6 grid
    if len(channel_data) > 0:
        fig, axes = plt.subplots(3, 6, figsize=(24, 12))
        fig.suptitle(f'Gaussian Fits for All Channels - {folder_timestamp}', fontsize=16)
        
        for ch_idx, (ch, ch_info) in enumerate(sorted(channel_data.items())):
            row, col = divmod(ch_idx, 6)
            if row >= 3:
                break
            
            ax = axes[row, col]
            data_vals = ch_info['data']
            dn = ch_info['dn']
            
            # Histogram
            vbinw = 1
            counts, bin_edges = np.histogram(data_vals, bins=range(min(data_vals), max(data_vals)+vbinw, vbinw))
            bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
            
            # Fit entire histogram with Gaussian
            amp, mean, sigma = np.nan, np.nan, np.nan
            fit_success = False

            initial_guess = [max(counts), np.mean(data_vals), np.std(data_vals)]

            try:
                popt, _ = curve_fit(
                    gaussian, bin_centers, counts, p0=initial_guess,
                    bounds=([0, min(data_vals), 0.1], [np.inf, max(data_vals), np.inf]),
                    maxfev=10000
                )
                amp, mean, sigma = popt
                fit_success = True

                # Smooth curve for plotting
                x_smooth = np.linspace(bin_centers[0], bin_centers[-1], 500)
                y_smooth = gaussian(x_smooth, *popt)
                ax.plot(x_smooth, y_smooth, 'r-', linewidth=2.5, label=f'Peak ADC={mean:.2f}, Amp={amp:.1f}')
            except:
                pass
            
            # Plot histogram
            ax.bar(bin_centers, counts, width=vbinw, alpha=0.6, color='blue', edgecolor='black')
            if fit_success:
                ax.plot(mean, amp, 'ro', markersize=8)
            
            # Add legend if fit was successful
            if fit_success:
                ax.legend(fontsize=7)
            
            ax.set_title(f'{dn}\nCH{ch:02d}', fontsize=8)
            ax.set_xlabel('Amplitude (ADC)', fontsize=7)
            ax.set_ylabel('Counts', fontsize=7)
            ax.grid(True, alpha=0.3)
            
            # Save histogram + Gaussian peak info to TXT
            txt_fp = os.path.join(rst_dir, f"{dn}_histogram_{folder_timestamp}.txt")
            with open(txt_fp, 'w') as tf:
                tf.write(f"# Histogram data for {dn} - Channel {ch}\n")
                tf.write("# Columns: BinCenter Counts\n")
                tf.write("#" + "-"*50 + "\n")
                
                # Write histogram bins
                for bc, ct in zip(bin_centers, counts):
                    tf.write(f"{bc:.2f} {ct:d}\n")
                
                # Write Gaussian peak as a separate line
                if fit_success:
                    tf.write(f"# Gaussian Fit Peak: Peak_ADC={mean:.2f}, Peak_Amplitude={amp:.2f}\n")
                else:
                    tf.write(f"# Gaussian Fit Peak: Peak_ADC=NaN, Peak_Amplitude=NaN (fit failed)\n")
        
        # Hide unused subplots
        for idx in range(len(channel_data), 18):
            row, col = divmod(idx, 6)
            axes[row, col].axis('off')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        # Save figure instead of showing
        fig_fp = os.path.join(rst_dir, f"Gaussian_Fits_{folder_timestamp}.png")
        plt.savefig(fig_fp, dpi=200)
        plt.close(fig)
        print(f"Saved plot: {fig_fp}")
