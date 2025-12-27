import os
import pandas as pd
import numpy as np
from viresclient import SwarmRequest
import datetime as dt
import matplotlib.pyplot as plt

# Settings
start_time = dt.datetime(2023, 3, 4, 12, 30)
end_time = dt.datetime(2023, 3, 4, 12, 32)
#collections = ["SW_OPER_MAGA_LR_1B", "SW_OPER_MAGB_LR_1B", "SW_OPER_MAGC_LR_1B"]
collections = ["SW_OPER_MAGA_LR_1B", "SW_OPER_MAGB_LR_1B", "SW_OPER_MAGC_LR_1B"]

# Create a figure with subplots for each satellite
fig, axs = plt.subplots(len(collections), 1, figsize=(20, 6 * len(collections)), sharex=True)
if len(collections) == 1:  # If there's only one collection, axs is not a list
    axs = [axs]

# Loop through each satellite collection and plot its data
for ax, collection in zip(axs, collections):
    # Request Swarm data for the current satellite
    request = SwarmRequest()
    request.set_collection(collection)
    request.set_products(measurements=["B_NEC"], models=["CHAOS"])
    data = request.get_between(start_time, end_time)
    df = data.as_dataframe()
    print(f"Data Headers for {collection}: ", df.columns)

    # Convert index to datetime for plotting
    time_array = pd.to_datetime(df.index)
    
    # Plot each component of the magnetic field
    ax.plot(time_array, np.vstack(df['B_NEC'])[:, 0], label='B_N (North-South)', color='cyan', linewidth = '4')
    ax.plot(time_array, np.vstack(df['B_NEC'])[:, 1], label='B_E (East-West)', color='magenta', linewidth = '4')
    ax.plot(time_array, np.vstack(df['B_NEC'])[:, 2], label='B_C (In-Out)', color='darkorange', linewidth = '4')
    
    ax.set_title(f'{collection} Magnetic Field Components')
    ax.legend()
    ax.grid(True)
    ax.set_ylabel('Magnetic Field Component (nT)')

# Set common x-axis label
axs[-1].set_xlabel('Time')
plt.tight_layout()


# Extract the directory path from one of the input files
output_dir = '/Users/clevenger/Projects/paper01/sop23_data/202303/04/'

# Create the output filename
output_filename = os.path.join(output_dir, 'swarm_mags_crossing3.png')

# Save the figure
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
