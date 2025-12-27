import h5py
import numpy as np

vvels_fn = '/Users/clevenger/Projects/paper01/events/20230227/vvels/outputs/20230227_vvels.h5'

with h5py.File(vvels_fn, "r") as h5:
    utimes = h5["Time/UnixTime"][:]   # shape (N, 2) or (N,)
    
# Convert to datetime64[s]
utimes_dt = utimes.astype("datetime64[s]")

# If shape is (N, 2): start and end time per index
if utimes_dt.ndim == 2 and utimes_dt.shape[1] == 2:
    for i, (t_start, t_end) in enumerate(utimes_dt):
        print(f"index {i}: start = {t_start}, end = {t_end}")
else:
    # Shape (N,): single timestamp per index
    for i, t in enumerate(utimes_dt):
        print(f"index {i}: time = {t}")

# Example: specific index (e.g., 10)
idx = 10
print("\nSpecific index:")
if utimes_dt.ndim == 2 and utimes_dt.shape[1] == 2:
    print(f"index {idx}: start = {utimes_dt[idx,0]}, end = {utimes_dt[idx,1]}")
else:
    print(f"index {idx}: time = {utimes_dt[idx]}")
