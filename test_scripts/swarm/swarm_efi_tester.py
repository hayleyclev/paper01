import numpy as np
import cdflib
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import cartopy.crs as ccrs

"""
Purpose:
    - load Swarm EFI TCT data from https://swarm-diss.eo.esa.int/#swarm/Advanced/Plasma_Data/2Hz_TII_Cross-track_Dataset
    - pull parameters from dataset
    - plot EFI TCT flows on 2D map
"""

# Give file paths and timing info
swarm_filename = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/SW_EXPT_EFIA_TCT02_20230227T042051_20230227T164506_0302.cdf'
starttime = np.datetime64('2023-02-27T08:37:00')
endtime = np.datetime64('2023-02-27T08:39:00')

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


# Plot PLASMA VELOCITY (SPACECRAFT COORDINATES)
fig = plt.figure()
ax = fig.add_subplot(311)
ax.plot(swarm_glat, Vixh, label='Vixh')
ax.plot(swarm_glat, Vixv, label='Vixv')
ax.axhline(y=0, color='k', linestyle=':')
ax.set_xlim([60., 68.])
ax.set_ylabel('Vix [m/s]')
ax.legend()
ax = fig.add_subplot(312)
ax.plot(swarm_glat, Viy, label='Viy')
ax.axhline(y=0, color='k', linestyle=':')
ax.set_xlim([60., 68.])
ax.set_ylabel('Viy [m/s]')
ax.legend()
ax = fig.add_subplot(313)
ax.plot(swarm_glat, Viz, label='Viz')
ax.set_xlim([60., 68.])
ax.axhline(y=0, color='k', linestyle=':')
ax.set_ylabel('Viz [m/s]')
ax.set_xlabel('Geodetic Latitude')
ax.legend()
plt.show()


# Plot SPACECRAFT VELOCITY
fig = plt.figure()
ax = fig.add_subplot(311)
ax.plot(swarm_glat, VsatN, label='VsatN')
ax.set_xlim([60., 68.])
ax.set_ylabel('VsatN [m/s]')
ax.legend()
ax = fig.add_subplot(312)
ax.plot(swarm_glat, VsatE, label='VsatE')
ax.set_xlim([60., 68.])
ax.set_ylabel('VsatE [m/s]')
ax.legend()
ax = fig.add_subplot(313)
ax.plot(swarm_glat, VsatC, label='VsatC')
ax.set_xlim([60., 68.])
ax.set_ylabel('VsatC [m/s]')
ax.set_xlabel('Geodetic Latitude')
ax.legend()
plt.show()


# Plot SPACECRAFT POSITION
fig = plt.figure()
ax = fig.add_subplot(311)
ax.plot(swarm_glat)
ax.set_ylabel('GLAT')
ax.legend()
ax = fig.add_subplot(312)
ax.plot(swarm_glon)
ax.set_ylabel('GLON')
ax.legend()
ax = fig.add_subplot(313)
ax.plot(swarm_galt)
ax.set_ylabel('GALT')
plt.show()


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
fig = plt.figure()
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
plt.show()


# A few TRIAL ROTATIONS
VsE = 0.
VsN = -1.
VsC = 0.
Vs_ct = np.array([VsN, -VsE, 0.])
R = np.array([[VsE, VsN, -VsC*VsE],
              [VsN, -VsE, -VsC*VsN],
              [-VsC, 0., VsC**2-1]])
print(R)
Vi = np.array([100., 0., 0.])
swarm_vel = np.einsum('...ij,...j->...i', R, Vi)
print(swarm_vel)
VE = np.array([0., 100., 0.])
pfisr_proj_vel = np.einsum('i,i->', VE, Vs_ct)
print(pfisr_proj_vel)
