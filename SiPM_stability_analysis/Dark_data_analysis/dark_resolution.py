import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# Define paths
rootdir = "/home/koloina/BNL_Work/Copy/SiPM_LED_hdf5_share/SiPM"
output_hdf5 = os.path.join(rootdir, "Dark_analysis.hdf5")
plot_dir = os.path.join(rootdir, "Resolution_DR")
ascii_dir = os.path.join(plot_dir, "ASCII")
os.makedirs(plot_dir, exist_ok=True)
os.makedirs(ascii_dir, exist_ok=True)

# CSV output
csv_file = os.path.join(plot_dir, "resolution_data.csv")
all_results = []  # store data for CSV

# Read HDF5 file and plot resolution vs time
with h5py.File(output_hdf5, 'r') as f:
    for sipmno in f.keys():
        times = []
        resolutions = []
        gain_values = []
        fwhm_values = []
        datetime_values = []

        for dt_str in f[sipmno].keys():
            try:
                # Parse timestamp from dataset
                dt = datetime.strptime(dt_str, "%Y_%m_%d_%H").replace(
                    tzinfo=ZoneInfo("America/New_York")
                )
                timestamp = dt.timestamp()
                
                # Get peaks and compute resolution
                peaks = f[sipmno][dt_str]["peaks"][:]
                if len(peaks) < 2:
                    continue
                peak_centers = peaks["mu"]
                sigmas = peaks["sigma"]
                
                # Compute gain1
                gain1 = peak_centers[1] - peak_centers[0]
                
                # Ensure gain1 is within range
                if 100 <= gain1 <= 300:
                    fwhm_p1 = 2 * np.sqrt(2 * np.log(2)) * sigmas[0]
                    res = fwhm_p1 * 100 / gain1

                    if res > 13:
                        continue

                    times.append(timestamp)
                    resolutions.append(res)
                    gain_values.append(gain1)
                    fwhm_values.append(fwhm_p1)
                    datetime_values.append(dt)
                    
            except (ValueError, IndexError, KeyError):
                continue
        
        # Create plot if data exists
        if times and resolutions:
            times = np.array(times)
            resolutions = np.array(resolutions)
            hours = (times - times[0]) / 3600  # Convert seconds to hours
            mean_res = np.mean(resolutions)
            normalized_res = resolutions / mean_res

            # ------------------------
            # Save ASCII per-channel
            # ------------------------
            res_file = os.path.join(ascii_dir, f"resolution_vs_time_{sipmno}.txt")
            norm_file = os.path.join(ascii_dir, f"normalized_resolution_vs_time_{sipmno}.txt")

            # Save resolution
            with open(res_file, "w") as f_out:
                f_out.write("# Datetime\tHours\tResolution(%)\n")
                for dt, hr, res in zip(datetime_values, hours, resolutions):
                    f_out.write(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}\t{hr:.6f}\t{res:.6f}\n")

            # Save normalized resolution
            with open(norm_file, "w") as f_out:
                f_out.write("# Datetime\tHours\tNormalized_Resolution\n")
                for dt, hr, norm in zip(datetime_values, hours, normalized_res):
                    f_out.write(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}\t{hr:.6f}\t{norm:.6f}\n")

            print(f"Saved ASCII files for {sipmno}: {res_file}, {norm_file}")

            # ------------------------
            # Plotting
            # ------------------------
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, 
                                           gridspec_kw={'height_ratios': [2, 1]})

            # --- Top plot: Resolution vs Time ---
            ax1.plot(hours, resolutions, 'x-', label=f"{sipmno}")
            ax1.axhline(mean_res, color='red', linestyle='--', label=f"Mean = {mean_res:.2f}%")
            ax1.set_ylabel("Resolution (%)")
            ax1.set_ylim(mean_res - 3, mean_res + 3)
            ax1.set_title(f"Resolution vs Time for {sipmno}")
            ax1.legend()
            ax1.grid(True)

            # --- Bottom plot: Normalized Resolution ---
            ax2.set_ylim(0.5, 1.5)
            ax2.plot(hours, normalized_res, '+-')
            ax2.axhline(1.0, color='red', linestyle='--')
            ax2.set_xlabel("Hours")
            ax2.set_ylabel("Normalized")
            ax2.set_title("Normalized Resolution")
            ax2.grid(True)

            plt.tight_layout()

            # Save plot
            plot_filename = os.path.join(plot_dir, f"resolution_vs_time_{sipmno}.png")
            plt.savefig(plot_filename, bbox_inches='tight', dpi=300)
            plt.close()
            print(f"Saved plot for {sipmno} at {plot_filename}")

            # --- Save results for CSV ---
            for t, hr, res, g, fwhm in zip(times, datetime_values, resolutions, gain_values, fwhm_values):
                all_results.append({
                    "SiPM": sipmno,
                    "Datetime": hr.strftime("%Y-%m-%d %H:%M:%S"),
                    "HoursSinceStart": (t - times[0]) / 3600,
                    "Resolution(%)": res,
                    "Gain": g,
                    "FWHM": fwhm
                })

# Save all results into CSV
df = pd.DataFrame(all_results)
df.to_csv(csv_file, index=False)
print(f"\nSaved all results to {csv_file}")
