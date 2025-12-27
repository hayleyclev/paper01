from netCDF4 import Dataset

def read_nc_headers(nc_file):
    """Reads and prints the headers of a NetCDF file."""
    with Dataset(nc_file, 'r') as ds:
        print("\n=== GLOBAL ATTRIBUTES ===")
        for attr in ds.ncattrs():
            print(f"{attr}: {ds.getncattr(attr)}")

        print("\n=== DIMENSIONS ===")
        for dim_name, dim in ds.dimensions.items():
            print(f"{dim_name}: length={len(dim)} {'(unlimited)' if dim.isunlimited() else ''}")

        print("\n=== VARIABLES ===")
        for var_name, var in ds.variables.items():
            print(f"\nVariable: {var_name}")
            print(f"  Dimensions: {var.dimensions}")
            print(f"  Shape: {var.shape}")
            print(f"  Datatype: {var.datatype}")
            for attr in var.ncattrs():
                print(f"    {attr}: {var.getncattr(attr)}")

if __name__ == "__main__":
    nc_file = input("Enter the full path to the NetCDF file: ").strip()
    try:
        read_nc_headers(nc_file)
    except FileNotFoundError:
        print(f"Error: File not found at {nc_file}")
    except Exception as e:
        print(f"Error reading file: {e}")
