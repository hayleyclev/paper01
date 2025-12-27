from netCDF4 import Dataset

file_path = "/Users/clevenger/Projects/paper01/events/20230227/lompe/outputs/cases/17/2023-02-27_083500.nc"

with Dataset(file_path, "r") as nc:
    print("Dimensions:")
    for dim in nc.dimensions:
        print(f"  {dim}: size={len(nc.dimensions[dim])}")
    
    print("\nVariables:")
    for var in nc.variables:
        print(f"  {var}: shape={nc.variables[var].shape}, dtype={nc.variables[var].dtype}")
    
    print("\nGlobal Attributes:")
    for attr in nc.ncattrs():
        print(f"  {attr}: {getattr(nc, attr)}")
