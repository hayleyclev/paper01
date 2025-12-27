import sys
import h5py
import numpy as np


def collect_datasets(h5file):
    """Return dict of dataset_name -> dataset object"""
    datasets = {}

    def visitor(name, obj):
        if isinstance(obj, h5py.Dataset):
            datasets[name] = obj

    h5file.visititems(visitor)
    return datasets


def print_dataset(name, dset):
    data = dset[...]

    print(f"\n{name}")
    print("-" * len(name))
    print(f"shape = {data.shape}")
    print(f"dtype = {data.dtype}")

    if np.issubdtype(data.dtype, np.number):
        print(f"min   = {np.nanmin(data)}")
        print(f"max   = {np.nanmax(data)}")

    # Pretty printing
    if data.ndim == 0:
        print(f"value = {data}")
    elif data.ndim == 1:
        print("values:")
        print(data)
    elif data.ndim == 2:
        nx, ny = data.shape
        cx, cy = nx // 2, ny // 2
        print("center 5x5 slice:")
        print(data[cx-2:cx+3, cy-2:cy+3])
    else:
        print("Data has >2 dimensions; showing first element:")
        print(data[0])


def main():
    if len(sys.argv) != 2:
        print("Usage: python h5_var_reader.py <file.h5>")
        sys.exit(1)

    filename = sys.argv[1]

    with h5py.File(filename, "r") as f:
        datasets = collect_datasets(f)

        print(f"\n=== Datasets in {filename} ===\n")
        for name, dset in datasets.items():
            print(f"{name:20s} shape={dset.shape}, dtype={dset.dtype}")

        print("\nType dataset name to view it.")
        print("Type 'q' to quit.\n")

        while True:
            choice = input("Variable name > ").strip()

            if choice.lower() in ("q", "quit", "exit"):
                break

            if choice not in datasets:
                print("Dataset not found. Try again.")
                continue

            print_dataset(choice, datasets[choice])


if __name__ == "__main__":
    main()
