import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ----------------------------
# Paths
# ----------------------------
rootdir = "/data/disk1/koloina/waveform_fitting/SIPM/Final_plots/"
hdf5_path = os.path.join(rootdir, "LED_Analysis_Final.hdf5")
output_dir = os.path.join(rootdir, "Envelope_mu_normalized_plots")
os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Helper function
# ----------------------------
def extract_envelope_data(hdf5_path):
    data = {}
    with h5py.File(hdf5_path, "r") as f:
        for sipm in f.keys():
            hv_prefix = sipm.split("_")[0]
            if hv_prefix not in data:
                data[hv_prefix] = {}
            for femb in f[sipm].keys():
                for timestamp in f[sipm][femb].keys():
                    try:
                        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        env_mu = f[sipm][femb][timestamp]["envelope_mu"][()]
                        if np.isnan(env_mu).any():
                            continue
                        if sipm not in data[hv_prefix]:
                            data[hv_prefix][sipm] = []
                        data[hv_prefix][sipm].append((dt, env_mu[0]))
                    except Exception:
                        continue
    return data

# ----------------------------
# Extract data
# ----------------------------
data = extract_envelope_data(hdf5_path)

# ----------------------------
# Plot normalized envelope μ per HV
# ----------------------------
for hv, channels in data.items():
    fig, axes = plt.subplots(6, 3, figsize=(18, 14), sharex=True)
    axes = axes.flatten()

    # Collect all timestamps to define zero-hour reference
    all_times = []
    for ch_name, values in channels.items():
        times = [v[0] for v in values]
        all_times.extend(times)
    if not all_times:
        print(f"No data for {hv}")
        continue
    t0 = min(all_times)

    # Plot each channel
    for i, (ch_name, values) in enumerate(sorted(channels.items())[:18]):  # only first 18 subplots
        ax = axes[i]
        values = sorted(values, key=lambda x: x[0])
        times = [(v[0] - t0).total_seconds() / 3600 for v in values]
        env_mu = np.array([v[1] for v in values])

        if len(env_mu) == 0:
            ax.axis("off")
            continue

        mean_mu = np.nanmean(env_mu)
        if mean_mu == 0 or np.isnan(mean_mu):
            ax.axis("off")
            continue

        norm_mu = env_mu / mean_mu

        ax.plot(times, norm_mu, marker="o", markersize=3, linewidth=1)
        ax.set_title(ch_name, fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_ylabel("Normalized PDE")
        ax.set_xlabel("Hours")
        #ax.set_ylim(0.8, 1.2)  # adjust range if needed

    # Turn off unused subplots
    for j in range(len(channels), len(axes)):
        axes[j].axis("off")

    fig.suptitle(f"{hv} – Normalized Envelope μ vs Time", fontsize=14)
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(os.path.join(output_dir, f"{hv}_Envelope_mu_vs_Time_normalized.png"), dpi=200)
    plt.close(fig)
    print(f"Saved normalized plot for {hv}")
