import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import h5py
import cdflib
from matplotlib.animation import FuncAnimation
import pandas as pd

def load_swarm_data(swarm_filename, starttime, endtime):
    v = cdflib.CDF(swarm_filename)
    swarm_time = cdflib.epochs.CDFepoch.to_datetime(v.varget('Timestamp'))

    stidx = np.argmin(np.abs(starttime.astype('datetime64[s]').astype(int) - swarm_time.astype('datetime64[s]').astype(int)))
    etidx = np.argmin(np.abs(endtime.astype('datetime64[s]').astype(int) - swarm_time.astype('datetime64[s]').astype(int)))

    # Ensure indices are within the valid range
    num_records = len(swarm_time)
    stidx = max(0, min(stidx, num_records - 1))
    etidx = max(0, min(etidx, num_records - 1))

    if stidx > etidx:
        stidx, etidx = etidx, stidx

    swarm_time = swarm_time[stidx:etidx+1]
    swarm_utime = swarm_time.astype('datetime64[s]').astype(int)

    # Read variables
    variables = ['Quality_flags', 'Calibration_flags', 'Vixh', 'Vixv', 'Viy', 'Viz', 'Latitude', 'Longitude', 'Radius']
    data = {}
    for var in variables:
        data[var] = v.varget(var, startrec=stidx, endrec=etidx)

    # Apply quality flags
    for vel in ['Vixh', 'Vixv', 'Viy', 'Viz']:
        data[vel][data['Quality_flags'] < 1] = np.nan

    # Calculate altitude
    data['galt'] = data['Radius'] / 1000. - 6371.

    return {
        'time': swarm_utime,
        'glat': data['Latitude'],
        'glon': data['Longitude'],
        'galt': data['galt'],
        'Vixh': data['Vixh'],
        'Vixv': data['Vixv'],
        'Viy': data['Viy'],
        'Viz': data['Viz']
    }

def plot_3d_composite(h5file, swarm_data, time_range, alt_range):
    with h5py.File(h5file, 'r') as h5:
        times = h5['Time/UnixTime'][:, 0]
        lats = h5['Geomag/Latitude'][:]
        lons = h5['Geomag/Longitude'][:]
        alts = h5['Geomag/Altitude'][:]
        dens = h5['FittedParams/Ne'][:]
        
        site_lat = h5['Site/Latitude'][()]
        site_lon = h5['Site/Longitude'][()]

    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Filter out NaN and Inf values
    valid_lons = lons[np.isfinite(lons)]
    valid_lats = lats[np.isfinite(lats)]
    valid_alts = alts[np.isfinite(alts)]

    # Plot PFISR beams once outside the update loop
    for beam in range(lats.shape[0]):
        x = lons[beam]
        y = lats[beam]
        z = alts[beam] / 1000  # Convert to km
        
        # Use a single color for each beam, and only plot finite values
        finite_mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
        ax.scatter(x[finite_mask], y[finite_mask], z[finite_mask], c='blue', s=10, alpha=0.5)

    # Initialize Swarm satellite plot
    swarm_plot, = ax.plot([], [], [], 'r*', markersize=10)

    def update(frame):
        # Update Swarm satellite position
        swarm_time_idx = np.argmin(np.abs(swarm_data['time'] - times[frame]))
        swarm_x = swarm_data['glon'][swarm_time_idx]
        swarm_y = swarm_data['glat'][swarm_time_idx]
        swarm_z = swarm_data['galt'][swarm_time_idx]

        swarm_plot.set_data(swarm_x, swarm_y)
        swarm_plot.set_3d_properties(swarm_z)

        ax.set_title(f"Time: {pd.to_datetime(times[frame], unit='s')}")
        
        return swarm_plot,

    # Set axis limits using only finite values
    ax.set_xlim(np.nanmin(valid_lons), np.nanmax(valid_lons))
    ax.set_ylim(np.nanmin(valid_lats), np.nanmax(valid_lats))
    ax.set_zlim(max(np.nanmin(valid_alts)/1000, alt_range[0]), min(np.nanmax(valid_alts)/1000, alt_range[1]))
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_zlabel('Altitude (km)')

    ani = FuncAnimation(fig, update, frames=range(len(times)), interval=200, blit=True)

    return ani

# Main execution
if __name__ == "__main__":
    # File paths and time range
    filename_lp = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/20230227.002_lp_5min-fitcal.h5'
    swarm_filename = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/SW_EXPT_EFIA_TCT02_20230227T042051_20230227T164506_0302.cdf'
    starttime = np.datetime64('2023-02-27T08:37:00')
    endtime = np.datetime64('2023-02-14T08:39:00')
    alt_range = (100, 500)  # km

    # Load Swarm data
    swarm_data = load_swarm_data(swarm_filename, starttime, endtime)

    # Create and save animation
    animation = plot_3d_composite(filename_lp, swarm_data, (starttime, endtime), alt_range)
    animation.save('/Users/clevenger/Projects/paper01/sop23_data/202302/27/crossing1.gif', writer='pillow', fps=5)
    plt.show()
    
    print("Animation saved as 3d_composite_with_swarm.gif")
