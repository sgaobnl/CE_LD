#----------------------------
Before use, run the code SiPm_trigger_data_analysis.py . You should get a .hdf5 file that contains the peaks data (centers, amplitudes, fwhm) , resolution, SNR and PDE.
#----------------------------
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

#Path of the .hdf5 file to analyse
hdf5_path = os.path.join(rootdir, "AnalysisResults.hdf5")
#Create an output directory to store the plots
output_dir = os.path.join(rootdir, "gain_plots_timeslots")
os.makedirs(output_dir, exist_ok=True)

#Target hours
target_hours = [0, 8, 21]
colors = {0: "#084594", 8: "purple", 21: "black"}
labels = {0: "00h", 8: "08h", 21: "21h"}

with h5py.File(hdf5_path, "r") as f:
    for sipm in f.keys():
        for ufemb in f[sipm].keys():
            time_list = []
            gain2_list = []
            gain3_list = []
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
                if len(fitted_centers) < 4:
                    continue

                gain2 = fitted_centers[2] - fitted_centers[1]
                gain3 = fitted_centers[3] - fitted_centers[2]

                if gain2 < 100:
                    gain2 = np.nan
                if gain3 < 100:
                    gain3 = np.nan

                time_list.append(dt)
                hour_list.append(dt.hour)
                gain2_list.append(gain2)
                gain3_list.append(gain3)

            if len(time_list) == 0:
                continue

            time_list, hour_list, gain2_list, gain3_list = zip(
                *sorted(zip(time_list, hour_list, gain2_list, gain3_list))
            )
            hours_since_start = [(t - time_list[0]).total_seconds() / 3600.0 for t in time_list]

            plt.figure(figsize=(12, 5))

            # Plot each time slot with its own color
            for hr in target_hours:
                idx = [i for i, h in enumerate(hour_list) if h == hr]
                plt.plot(
                    [hours_since_start[i] for i in idx],
                    [gain2_list[i] for i in idx],
                    "+", color=colors[hr], label=f"Gain2 {labels[hr]}"
                )
                plt.plot(
                    [hours_since_start[i] for i in idx],
                    [gain3_list[i] for i in idx],
                    "x", color=colors[hr], label=f"Gain3 {labels[hr]}"
                )

            plt.xlabel("Hours since first timestamp")
            plt.ylabel("Gain (ADC units)")
            plt.title(f"{sipm} - {ufemb} Gains at 00h, 08h, 21h")
            plt.grid(True, ls="--", alpha=0.6)

            # Move legend outside the plot on the right
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
            plt.tight_layout(rect=[0, 0, 0.8, 1])  # Adjust space for legend

            plot_fp = os.path.join(output_dir, f"{sipm}_{ufemb}_gains_timeslots.png")
            plt.savefig(plot_fp, bbox_inches="tight")
            plt.close()

            print(f"Saved plot: {plot_fp}")
