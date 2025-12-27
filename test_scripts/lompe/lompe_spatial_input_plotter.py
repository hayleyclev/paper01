import matplotlib.pyplot as plt
import numpy as np
import h5py
import pandas as pd
from pyproj import Geod
import cdflib

def geodetic_displacement(lats, lons, ref_lat, ref_lon):
    g = Geod(ellps='WGS84')
    az, _, dist = g.inv(np.full_like(lons, ref_lon), np.full_like(lats, ref_lat), lons, lats)
    dx = dist * np.sin(np.radians(az)) / 1000
    dy = dist * np.cos(np.radians(az)) / 1000
    return dx, dy

def plot_3d_vlos_centered(h5file, swarm_cdf, time_point, alt_range_km=(0, 500), region_km=250, time_pad_min=5):
    # === Load PFISR ===
    with h5py.File(h5file, 'r') as h5:
        times = h5['Time/UnixTime'][:, 0]
        lats = h5['Geomag/Latitude'][:]
        lons = h5['Geomag/Longitude'][:]
        alts = h5['Geomag/Altitude'][:] / 1000
        fits = h5['FittedParams/Fits'][:]
        site_lat = h5['Site/Latitude'][()]
        site_lon = h5['Site/Longitude'][()]

    times_dt = pd.to_datetime(times, unit='s')
    time_idx = np.argmin(np.abs(times_dt - time_point))
    vlos = fits[time_idx, :, :, 0, 3]

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    for beam in range(lats.shape[0]):
        lat, lon, alt, v = lats[beam], lons[beam], alts[beam], vlos[beam]
        x, y = geodetic_displacement(lat, lon, site_lat, site_lon)
        ax.scatter(x, y, alt, c=v, cmap='bwr', s=12, vmin=-500, vmax=500)

    # === Load Swarm CDF ===
    v = cdflib.CDF(swarm_cdf)
    swarm_time = cdflib.epochs.CDFepoch.to_datetime(v.varget('Timestamp'))
    dt64 = np.array(swarm_time).astype('datetime64[s]')
    pad = np.timedelta64(time_pad_min, 'm')
    mask = (dt64 >= time_point - pad) & (dt64 <= time_point + pad)

    if not np.any(mask):
        print("No Swarm data within time window.")
    else:
        swarm_lat = v.varget('Latitude')[mask]
        swarm_lon = v.varget('Longitude')[mask]
        r = v.varget('Radius')[mask]
        swarm_alt = r / 1000.0 - 6371.0
        VsatN, VsatE, VsatC = v.varget('VsatN')[mask], v.varget('VsatE')[mask], v.varget('VsatC')[mask]
        Vixh, Vixv, Viy, Viz = [v.varget(k)[mask] for k in ['Vixh', 'Vixv', 'Viy', 'Viz']]
        qf = v.varget('Quality_flags')[mask]
        Vixh[qf < 1] = np.nan; Vixv[qf < 1] = np.nan; Viy[qf < 1] = np.nan; Viz[qf < 1] = np.nan

        # === Rotate into ENU frame ===
        Vsat_mag = np.sqrt(VsatN**2 + VsatE**2 + VsatC**2)
        VsN, VsE, VsC = VsatN/Vsat_mag, VsatE/Vsat_mag, VsatC/Vsat_mag

        s = VsatC.shape
        R = np.array([[VsE, VsN, -VsC*VsE],
                      [VsN, -VsE, -VsC*VsN],
                      [-VsC, np.zeros(s), VsC**2 - 1]]).transpose((2,0,1))
        Vi = np.array([(Vixh + Vixv)/2., Viy, Viz]).T
        swarm_vel = np.einsum('...ij,...j->...i', R, Vi)

        # === Project Swarm positions to PFISR-centered local coords ===
        sx, sy = geodetic_displacement(swarm_lat, swarm_lon, site_lat, site_lon)
        sz = swarm_alt
        swarm_speed = np.linalg.norm(swarm_vel, axis=1)

        ax.quiver(sx, sy, sz,
                  swarm_vel[:, 0], swarm_vel[:, 1], swarm_vel[:, 2],
                  length=10, normalize=True, color='k', alpha=0.7, label='Swarm TII vectors')

        sc = ax.scatter(sx, sy, sz, c=swarm_speed, cmap='cool', s=8, alpha=0.6)
        fig.colorbar(sc, ax=ax, label='Swarm TII Speed (m/s)')

    # === Final Formatting ===
    ax.set_xlim(-region_km, region_km)
    ax.set_ylim(-region_km, region_km)
    ax.set_zlim(alt_range_km[0], alt_range_km[1])
    ax.set_xlabel("East (km)")
    ax.set_ylabel("North (km)")
    ax.set_zlabel("Altitude (km)")
    ax.set_title(f"PFISR Vlos + Swarm TII\n{time_point}")
    mappable = ax.scatter([], [], [], c=[], cmap='bwr', vmin=-500, vmax=500)
    fig.colorbar(mappable, ax=ax, label='PFISR Vlos (m/s)')
    plt.tight_layout()
    plt.show()

filename_lp = '/Users/clevenger/Projects/paper01/sop23_data/202303/22/20230322.003_lp_3min-fitcal.h5'
swarm_cdf = '/Users/clevenger/Projects/paper01/sop23_data/202303/22/SW_EXPT_EFIB_TCT02_20230322T005252_20230322T132507_0302.cdf'
time_point = np.datetime64('2023-03-22T08:58:00')

plot_3d_vlos_centered(filename_lp, swarm_cdf, time_point)
