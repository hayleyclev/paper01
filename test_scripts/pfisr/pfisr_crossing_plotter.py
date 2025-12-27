import numpy as np
import h5py
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates

filename_ac = '/Users/clevenger/Projects/paper01/sop23_data/202303/22/20230322.003_ac_3min-fitcal.h5'
filename_lp = '/Users/clevenger/Projects/paper01/sop23_data/202303/22/20230322.003_lp_3min-fitcal.h5'

start_time = np.datetime64('2023-03-22T08:30:00')
end_time = np.datetime64('2023-03-22T09:29:00')

def plot_beamcode(beamcode, filename_ac, filename_lp, start_time, end_time):
    with h5py.File(filename_lp, 'r') as h5:
        beamcodes = h5['BeamCodes'][:]
        bidx = np.where(beamcodes[:, 0] == beamcode)[0][0]
        alt_lp = h5['FittedParams/Altitude'][bidx,:]
        ne_lp = h5['FittedParams/Ne'][:,bidx,:]
        ti_lp = h5['FittedParams/Fits'][:,bidx,:,0,1]
        te_lp = h5['FittedParams/Fits'][:,bidx,:,-1,1]
        vlos_lp = h5['FittedParams/Fits'][:,bidx,:,0,3]
        utime_lp = h5['Time/UnixTime'][:,0]

    time_lp = utime_lp.astype('datetime64[s]')
    ne_lp = ne_lp[:,np.isfinite(alt_lp)]
    ti_lp = ti_lp[:,np.isfinite(alt_lp)]
    te_lp = te_lp[:,np.isfinite(alt_lp)]
    vlos_lp = vlos_lp[:,np.isfinite(alt_lp)]
    alt_lp = alt_lp[np.isfinite(alt_lp)]

    with h5py.File(filename_ac, 'r') as h5:
        beamcodes = h5['BeamCodes'][:]
        bidx = np.where(beamcodes[:, 0] == beamcode)[0][0]
        alt_ac = h5['FittedParams/Altitude'][bidx,:]
        ne_ac = h5['FittedParams/Ne'][:,bidx,:]
        ti_ac = h5['FittedParams/Fits'][:,bidx,:,0,1]
        te_ac = h5['FittedParams/Fits'][:,bidx,:,-1,1]
        vlos_ac = h5['FittedParams/Fits'][:,bidx,:,0,3]
        utime_ac = h5['Time/UnixTime'][:,0]

    time_ac = utime_ac.astype('datetime64[s]')
    ne_ac = ne_ac[:,np.isfinite(alt_ac)]
    ti_ac = ti_ac[:,np.isfinite(alt_ac)]
    te_ac = te_ac[:,np.isfinite(alt_ac)]
    vlos_ac = vlos_ac[:,np.isfinite(alt_ac)]
    alt_ac = alt_ac[np.isfinite(alt_ac)]

    cutoff_alt = 150.*1000.
    aidx_ac = np.argmin(np.abs(alt_ac-cutoff_alt))
    aidx_lp = np.argmin(np.abs(alt_lp-cutoff_alt))

    fig = plt.figure(figsize=(10,10))
    gs = gridspec.GridSpec(4,1)

    # Plot Electron Density
    ax = fig.add_subplot(gs[0])
    c = ax.pcolormesh(time_ac, alt_ac[:aidx_ac], ne_ac[:,:aidx_ac].T, vmin=0., vmax=4.e11, cmap='viridis')
    c = ax.pcolormesh(time_lp, alt_lp[aidx_lp:], ne_lp[:,aidx_lp:].T, vmin=0., vmax=4.e11, cmap='viridis')
    ax.set_ylabel('Altitude (m)')
    ax.set_xlim(start_time, end_time)
    fig.colorbar(c, label=r'Electron Density (m$^{-3}$)')

    # Plot Ion Temperature
    ax = fig.add_subplot(gs[1])
    c = ax.pcolormesh(time_ac, alt_ac[:aidx_ac], ti_ac[:,:aidx_ac].T, vmin=0., vmax=3.e3, cmap='magma')
    c = ax.pcolormesh(time_lp, alt_lp[aidx_lp:], ti_lp[:,aidx_lp:].T, vmin=0., vmax=3.e3, cmap='magma')
    ax.set_ylabel('Altitude (m)')
    ax.set_xlim(start_time, end_time)
    fig.colorbar(c, label=r'Ion Temperature (K)')

    # Plot Electron Temperature
    ax = fig.add_subplot(gs[2])
    c = ax.pcolormesh(time_ac, alt_ac[:aidx_ac], te_ac[:,:aidx_ac].T, vmin=0., vmax=5.e3, cmap='inferno')
    c = ax.pcolormesh(time_lp, alt_lp[aidx_lp:], te_lp[:,aidx_lp:].T, vmin=0., vmax=5.e3, cmap='inferno')
    ax.set_ylabel('Altitude (m)')
    ax.set_xlim(start_time, end_time)
    fig.colorbar(c, label=r'Electron Temperature (K)')

    # Plot Line-of-Site Velocity
    ax = fig.add_subplot(gs[3])
    c = ax.pcolormesh(time_ac, alt_ac[:aidx_ac], vlos_ac[:,:aidx_ac].T, vmin=-500., vmax=500., cmap='bwr')
    c = ax.pcolormesh(time_lp, alt_lp[aidx_lp:], vlos_lp[:,aidx_lp:].T, vmin=-500., vmax=500., cmap='bwr')
    ax.set_xlabel('Universal Time')
    ax.set_ylabel('Altitude (m)')
    ax.set_xlim(start_time, end_time)
    fig.colorbar(c, label=r'Line-of-Site Velocity (m/s)')

    # Format x-axis ticks
    for ax in fig.get_axes():
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

    plt.tight_layout()
    return fig

# Extract all unique beamcodes
with h5py.File(filename_lp, 'r') as h5:
    beamcodes = h5['BeamCodes'][:]
    unique_beamcodes = np.unique(beamcodes[:, 0])

# Extract the directory path from one of the input files
output_dir = os.path.dirname(filename_ac)

# Loop through all beamcodes, create and save plots
for beamcode in unique_beamcodes:
    fig = plot_beamcode(beamcode, filename_ac, filename_lp, start_time, end_time)
    
    # Create the output filename
    output_filename = os.path.join(output_dir, f'crossing_beam{int(beamcode)}.png')
    
    # Save the figure
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close(fig)  # Close the figure to free up memory
    print(f"Plot saved as: {output_filename}")
