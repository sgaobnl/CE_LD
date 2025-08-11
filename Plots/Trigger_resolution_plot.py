import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

#HDF5 with the data
hdf5_path = os.path.join(rootdir, "AnalysisResults.hdf5")
#Make a folder to store the plots
output_dir = os.path.join(rootdir, "resolution_plots_timeslots")
os.makedirs(output_dir, exist_ok=True)

target_hours = [0, 8, 21]
colors = {0: "#084594", 8: "purple", 21: "black"}
labels = {0: "00h", 8: "08h", 21: "21h"}

with h5py.File(hdf5_path, "r") as f:
    for sipm in f.keys():
        for ufemb in f[sipm].keys():
            time_list = []
            res2_list = []
            res3_list = []
            hour_list = []

            for date_str in sorted(f[sipm][ufemb].keys()):
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue

                if dt.hour not in target_hours:
                    continue

                dset = f[sipm][ufemb][date_str]
                fitted_centers = np.array(dset["fitted_centers"])
                fwhms = np.array(dset["fwhms"])
                if len(fitted_centers) < 4:
                    continue
                    
                gain2 = fitted_centers[2] - fitted_centers[1]
                gain3 = fitted_centers[3] - fitted_centers[2]

                if gain2 < 100:
                    gain2 = np.nan
                if gain3 < 100:
                    gain3 = np.nan

                res2 = fwhms[1] * 100 / gain2 if not np.isnan(gain2) else np.nan
                res3 = fwhms[1] * 100 / gain3 if not np.isnan(gain3) else np.nan

                # Skip if resolution is negative
                if (not np.isnan(res2) and res2 < 0) or (not np.isnan(res3) and res3 < 0):
                    continue

                time_list.append(dt)
                hour_list.append(dt.hour)
                res2_list.append(res2)
                res3_list.append(res3)

            if len(time_list) == 0:
                continue

            time_list, hour_list, res2_list, res3_list = zip(
                *sorted(zip(time_list, hour_list, res2_list, res3_list))
            )
            hours_since_start = [(t - time_list[0]).total_seconds() / 3600.0 for t in time_list]

            plt.figure(figsize=(12, 5))

            # Plot each time slot with its own color
            for hr in target_hours:
                idx = [i for i, h in enumerate(hour_list) if h == hr]
                plt.plot(
                    [hours_since_start[i] for i in idx],
                    [res2_list[i] for i in idx],
                    "-+", color=colors[hr], label=f"Res2 {labels[hr]}"
                )

          #You could also plot res3 by copy-pasting the code section above and changing res2 to res3
                
            plt.xlabel("Hours since first timestamp")
            plt.ylabel("Resolution (%)")
            plt.title(f"{sipm} - {ufemb} Resolutions at 00h, 08h, 21h")
            plt.grid(True, ls="--", alpha=0.6)

            # Move legend outside the plot on the right
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
            plt.tight_layout(rect=[0, 0, 0.8, 1])  # Adjust space for legend

            plot_fp = os.path.join(output_dir, f"{sipm}_{ufemb}_resolutions_timeslots.png")
            plt.savefig(plot_fp, bbox_inches="tight")
            plt.close()

            print(f"Saved plot: {plot_fp}")
