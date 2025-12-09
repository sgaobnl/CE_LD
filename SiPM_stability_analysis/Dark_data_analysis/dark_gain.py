import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from zoneinfo import ZoneInfo

# Define paths
rootdir = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/SiPM"
output_hdf5 = os.path.join(rootdir, "Dark_analysis.hdf5")
plot_dir = os.path.join(rootdir, "SiPM")
ascii_dir = os.path.join(rootdir, "ASCII")
os.makedirs(plot_dir, exist_ok=True)
os.makedirs(ascii_dir, exist_ok=True)

# Read HDF5 file and plot gain vs time
with h5py.File(output_hdf5, 'r') as f:
    for sipmno in f.keys():
        times = []
        gains = []
        for dt_str in f[sipmno].keys():
            try:
                # Parse timestamp from dataset
                dt = datetime.strptime(dt_str, "%Y_%m_%d_%H").replace(
                    tzinfo=ZoneInfo("America/New_York")
                )
                timestamp = dt.timestamp()
                
                # Get peaks and compute gain
                peaks = f[sipmno][dt_str]["peaks"][:]
                if len(peaks) < 2:
                    continue
                peak_centers = peaks["mu"]
                
                # Compute gain1 as peakcenter(1) - peakcenter(0)
                gain1 = peak_centers[1] - peak_centers[0]
                
                # Ensure gain1 is not negative and not above 400
                if 100 <= gain1 <= 500:
                    times.append(timestamp)
                    gains.append(gain1)
            except (ValueError, IndexError, KeyError):
                continue
        
        # Create subplot figure if data exists
        if times and gains:
            times = np.array(times)
            gains = np.array(gains)
            hours = (times - times[0]) / 3600  # Convert seconds to hours

            mean_gain = np.mean(gains)
            norm_gains = gains / mean_gain

            # --------------------
            # Save ASCII data files
            # --------------------
            gain_file = os.path.join(ascii_dir, f"gain_vs_time_{sipmno}.txt")
            norm_file = os.path.join(ascii_dir, f"normalized_gain_vs_time_{sipmno}.txt")

            np.savetxt(gain_file, np.column_stack([hours, gains]),
                       header="Hours\tGain", fmt="%.6f\t%.6f")
            np.savetxt(norm_file, np.column_stack([hours, norm_gains]),
                       header="Hours\tNormalized_Gain", fmt="%.6f\t%.6f")

            print(f"Saved ASCII files: {gain_file}, {norm_file}")

            # --------------------
            # Plotting
            # --------------------
            fig, axs = plt.subplots(2, 1, figsize=(10, 10), sharex=True)
  
            # --- Raw Gain vs Time ---
            axs[0].scatter(hours, gains, marker='x')
            axs[0].set_ylabel("Gain")
            axs[0].set_title(f"Gain vs Time for {sipmno}")
            axs[0].grid(True)
            axs[0].axhline(mean_gain, color='red', linestyle='--',
                           label=f"Mean gain = {mean_gain:.1f}")
            axs[0].legend()

            # --- Normalized Gain vs Time ---
            axs[1].scatter(hours, norm_gains, marker='x')
            axs[1].set_xlabel("Hours")
            axs[1].set_ylabel("Normalized Gain")
            axs[1].set_title(f"Normalized Gain vs Time for {sipmno}")
            axs[1].grid(True)
            axs[1].set_ylim(0.90, 1.10)
            axs[1].axhline(1.0, color='red', linestyle='--')

            fig.tight_layout()

            # Save subplot figure
            plot_filename = os.path.join(plot_dir, f"gain_and_normalized_vs_time_{sipmno}.png")
            plt.savefig(plot_filename, bbox_inches='tight', dpi=300)
            plt.close()
            print(f"Saved subplot figure for {sipmno} at {plot_filename}")
