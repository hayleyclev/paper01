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
swarm_filename = '/Users/clevenger/Projects/paper01/sop23_data/202303/22/SW_EXPT_EFIB_TCT02_20230322T005252_20230322T132507_0302.cdf'
starttime = np.datetime64('2023-03-22T08:00:00')
endtime = np.datetime64('2023-03-22T10:00:00')

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
plt.savefig('/Users/clevenger/Projects/paper01/sop23_data/202303/22/crossingb.png', dpi=300, bbox_inches='tight')
plt.show()
