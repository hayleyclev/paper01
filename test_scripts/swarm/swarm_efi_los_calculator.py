import numpy as np
import cdflib
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import cartopy.crs as ccrs

def lat_lon_alt_to_ecef(lat, lon, alt):
    # WGS84 ellipsoid constants
    a = 6378137.0  # semi-major axis
    e2 = 6.69437999014e-3  # first eccentricity squared
    
    lat, lon = np.radians(lat), np.radians(lon)
    N = a / np.sqrt(1 - e2 * np.sin(lat)**2)
    
    x = (N + alt) * np.cos(lat) * np.cos(lon)
    y = (N + alt) * np.cos(lat) * np.sin(lon)
    z = (N * (1 - e2) + alt) * np.sin(lat)
    
    return x, y, z

"""
Purpose:
    - load Swarm EFI TCT data from https://swarm-diss.eo.esa.int/#swarm/Advanced/Plasma_Data/2Hz_TII_Cross-track_Dataset
    - pull parameters from dataset
    - plot EFI TCT flows on 2D map
    - calculate and plot LOS vector
"""

# Give file paths and timing info
swarm_filename = '/Users/clevenger/Projects/paper01/events/20230214/real_data/swarm_EFI_TCT/SW_EXPT_EFIA_TCT02_20230214T030751_20230214T153406_0302.cdf'
starttime = np.datetime64('2023-02-14T09:15:00')
endtime = np.datetime64('2023-02-14T09:20:00')

# Create object to query dataset
v = cdflib.CDF(swarm_filename)
swarm_time = cdflib.epochs.CDFepoch.to_datetime(v.varget('Timestamp'))

# Find indices for time range
stidx = np.argmin(np.abs(starttime-swarm_time))
etidx = np.argmin(np.abs(endtime-swarm_time))
swarm_time = swarm_time[stidx:etidx+1]
swarm_utime = swarm_time.astype('datetime64[s]').astype(int)

# Identify quality flags to parse "bad" data
qf = v.varget('Quality_flags', startrec=stidx, endrec=etidx)
cf = v.varget('Calibration_flags', startrec=stidx, endrec=etidx)

# Read plasma velocities
Vixh = v.varget('Vixh', startrec=stidx, endrec=etidx)
Vixv = v.varget('Vixv', startrec=stidx, endrec=etidx)
Viy = v.varget('Viy', startrec=stidx, endrec=etidx)
Viz = v.varget('Viz', startrec=stidx, endrec=etidx)

# Mask/filter out flagged "bad" data
Vixh[qf<1] = np.nan
Vixv[qf<1] = np.nan
Viy[qf<1] = np.nan
Viz[qf<1] = np.nan

# Read satelite position and velocity
swarm_glat = v.varget('Latitude', startrec=stidx, endrec=etidx)
swarm_glon = v.varget('Longitude', startrec=stidx, endrec=etidx)
r = v.varget('Radius', startrec=stidx, endrec=etidx)
swarm_galt = r/1000. - 6371.
VsatN = v.varget('VsatN', startrec=stidx, endrec=etidx)
VsatE = v.varget('VsatE', startrec=stidx, endrec=etidx)
VsatC = v.varget('VsatC', startrec=stidx, endrec=etidx)

# Convert satellite position to ECEF coordinates
swarm_x, swarm_y, swarm_z = lat_lon_alt_to_ecef(swarm_glat, swarm_glon, swarm_galt)

# Calculate LOS vector
los_x = VsatE
los_y = VsatN
los_z = VsatC

# Normalize to get unit vector
los_magnitude = np.sqrt(los_x**2 + los_y**2 + los_z**2)
los_unit_x = los_x / los_magnitude
los_unit_y = los_y / los_magnitude
los_unit_z = los_z / los_magnitude

# Perform matrix rotation on velocity vectors
# Calculate satellite Ram direction unit vector
Vsat_mag = np.sqrt(VsatN**2 + VsatE**2 + VsatC**2)
VsN = VsatN/Vsat_mag
VsE = VsatE/Vsat_mag
VsC = VsatE/Vsat_mag

# Calculate velocity vectors in ENU coordinates
s = VsatC.shape
R = np.array([[VsE, VsN, -VsC*VsE],
              [VsN, -VsE, -VsC*VsN],
              [-VsC, np.zeros(s), VsC**2-1]]).transpose((2,0,1))
Vi = np.array([(Vixh+Vixv)/2., Viy, Viz]).T
swarm_vel = np.einsum('...ij,...j->...i', R, Vi)
swarm_vel_mag = np.linalg.norm(Vi[:,:2], axis=1)
print(Vi.shape, swarm_vel_mag.shape)

# Generate MAP OF ROTATED VECTORS
# generate figure
fig = plt.figure(figsize=(12, 8))
norm = Normalize(vmin=0, vmax=2000.)
# create map
proj = ccrs.AzimuthalEquidistant(central_longitude=-147, central_latitude=64)
ax = fig.add_subplot(111, projection=proj)
gl = ax.gridlines(draw_labels=True, zorder=1)
gl.right_labels = False
ax.coastlines()
ax.set_extent([-159., -135., 59., 71.], crs=ccrs.PlateCarree())

# NOTE: This function is needed due to an issue with cartopy where vectors are not scale/rotated correctly in some coordinate systems (see: https://github.com/SciTools/cartopy/issues/1179)
def scale_uv(lon, lat, u, v):
    us = u/np.cos(lat*np.pi/180.)
    vs = v
    sf = np.sqrt(u**2+v**2)/np.sqrt(us**2+vs**2)
    return us*sf, vs*sf

u, v = scale_uv(swarm_glon, swarm_glat, swarm_vel[:,0], swarm_vel[:,1])
Q = ax.quiver(swarm_glon, swarm_glat, u, v, swarm_vel_mag, norm=norm, cmap='cool', zorder=5, scale=10000, linewidth=2, color='k', transform=ccrs.PlateCarree())

ax.quiverkey(Q, 0.4, 0.1, 500, 'V=500m/s', labelpos='E', transform=ax.transAxes)

# Plot LOS vectors
u_los, v_los = scale_uv(swarm_glon, swarm_glat, los_unit_x, los_unit_y)
Q_los = ax.quiver(swarm_glon, swarm_glat, u_los, v_los,
                  color='r', scale=20, width=0.004,
                  transform=ccrs.PlateCarree())
ax.quiverkey(Q_los, 0.4, 0.05, 1, 'LOS', labelpos='E', transform=ax.transAxes)

plt.title('Swarm Velocity and LOS Vectors')
plt.show()
