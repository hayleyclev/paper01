import matplotlib.pyplot as plt
import numpy as np
import h5py
import pandas as pd

def plot_3d_composite(h5file, time_point, alt_range):
    with h5py.File(h5file, 'r') as h5:
        times = h5['Time/UnixTime'][:,0]
        lats = h5['Geomag/Latitude'][:]
        lons = h5['Geomag/Longitude'][:]
        alts = h5['Geomag/Altitude'][:]
        ne = h5['FittedParams/Ne'][:]
        fits = h5['FittedParams/Fits'][:]

        site_lat = h5['Site/Latitude'][()]
        site_lon = h5['Site/Longitude'][()]
    
    times_dt = pd.to_datetime(times, unit='s')
    
    time_idx = np.argmin(np.abs(times_dt - time_point))
    
    ti = fits[:, :, :, 0, 1]
    te = fits[:, :, :, -1, 1]
    vlos = fits[:, :, :, 0, 3]

    fig = plt.figure(figsize=(20, 15))
    axs = [fig.add_subplot(221, projection='3d'),
           fig.add_subplot(222, projection='3d'),
           fig.add_subplot(223, projection='3d'),
           fig.add_subplot(224, projection='3d')]

    for i, (ax, data, title, cmap) in enumerate(zip(axs, 
                                                    [ne, ti, te, vlos],
                                                    ['Ne', 'Ti', 'Te', 'Vlos'],
                                                    ['viridis', 'magma', 'inferno', 'bwr'])):
        for beam in range(lats.shape[0]):
            x = lons[beam]
            y = lats[beam]
            z = alts[beam] / 1000  # Convert to km
            c = data[time_idx, beam, :]
            
            scatter = ax.scatter(x, y, z, c=c, cmap=cmap, s=10)
        
        ax.set_zlim(alt_range[0], alt_range[1])
        ax.set_title(f"{title} - Time: {pd.to_datetime(times[time_idx], unit='s')}")
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Altitude (km)')
        
        plt.colorbar(scatter, ax=ax, label=title)

    fig.suptitle(f"PFISR Data - Time: {pd.to_datetime(times[time_idx], unit='s')}", fontsize=16)
    plt.savefig('/Users/clevenger/Projects/paper01/events/20230227/amisrsynthdata/fac_run/fac_precip_composite.png', dpi=300, bbox_inches='tight')
    plt.close()
    #plt.show()
    
# RUN
filename_lp = '/Users/clevenger/Projects/paper01/events/20230227/amisrsynthdata/fac_run/paper01_event01_fac_precip.h5'
time_point = np.datetime64('2023-02-27T08:37:00')
alt_range = (100, 500)  # km

plot_3d_composite(filename_lp, time_point, alt_range)
