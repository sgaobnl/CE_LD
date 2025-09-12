import h5py
import matplotlib.pyplot as plt
import os

def main():
    filename = 'femb1_darkrate_vs_time.hdf5' #add your filename
    output_dir = 'plots_femb1_darkrate_vs_time' #add an output directory to store the plots (optional)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    with h5py.File(filename, 'r') as f:
        for group_name in f:
            avg_values = []
            group = f[group_name]

            dataset_names = list(group.keys())  # Use dataset order as-is
            for dataset_name in dataset_names:
                dataset = group[dataset_name]
                if isinstance(dataset, h5py.Dataset) and 'Avg(<20Hz)' in dataset.attrs:
                    avg_20hz = dataset.attrs['Avg(<20Hz)']
                    avg_values.append(avg_20hz)

            if not avg_values:
                print(f"No valid datasets with 'Avg(<20Hz)' found in group {group_name}. Skipping plot.")
                continue

            # Print number of hours (i.e. time points) (optional)
            num_hours = len(avg_values)
            print(f"Group '{group_name}' contains {num_hours} hour(s) of data.")

            # Create x-axis as simple hour steps: 0, 1, 2, ...
            time_hours = list(range(num_hours))

            # Plot
            plt.figure(figsize=(10, 6))
            plt.plot(time_hours, avg_values, marker='o', linestyle='-')
            plt.title(f'Avg(<20Hz) vs Duration (hours) for Group: {group_name}')
            plt.xlabel('Duration (hours)')
            plt.ylabel('Avg(<20Hz)')
            plt.grid(True)

            # Save plot
            safe_group_name = group_name.replace('/', '_')
            filepath = os.path.join(output_dir, f'Avg_20Hz_{safe_group_name}.png')
            plt.savefig(filepath)
            plt.close()

            print(f"Saved plot for group '{group_name}' as '{filepath}'")

if __name__ == "__main__":
    main()
