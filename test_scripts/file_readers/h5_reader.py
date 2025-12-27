import sys
import h5py


def print_attrs(obj, indent):
    """Print HDF5 attributes for a group or dataset."""
    for key, val in obj.attrs.items():
        print(f"{indent}  [attr] {key}: {val}")


def visit(name, obj):
    """Callback for visiting HDF5 objects."""
    indent = "  " * name.count("/")

    if isinstance(obj, h5py.Group):
        print(f"{indent}[Group] {name}")
        print_attrs(obj, indent)

    elif isinstance(obj, h5py.Dataset):
        print(
            f"{indent}[Dataset] {name} "
            f"shape={obj.shape}, dtype={obj.dtype}"
        )
        print_attrs(obj, indent)


def main():
    if len(sys.argv) != 2:
        print("Usage: python h5_reader.py <file.h5>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with h5py.File(filename, "r") as f:
            print(f"\n=== HDF5 structure: {filename} ===\n")
            f.visititems(visit)
    except Exception as e:
        print(f"Error opening file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
