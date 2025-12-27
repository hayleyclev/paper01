import numpy as np
import cdflib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Import for 3D plotting

"""
Purpose:
    - load Swarm EFI TCT data from a CDF file
    - pull parameters from dataset
    - plot the satellite trajectory in geodetic coordinates (lat, lon, alt)
"""

# Inputs - Swarm A
swarm_a_filename = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/SW_EXPT_EFIA_TCT02_20230227T042051_20230227T164506_0302.cdf'
starttime = np.datetime64('2023-02-27T08:37:00')
endtime = np.datetime64('2023-02-27T10:00:00')

# Create object to query dataset
v_a = cdflib.CDF(swarm_a_filename)
swarm_a_time = cdflib.epochs.CDFepoch.to_datetime(v_a.varget('Timestamp'))

# Find indices for time range
stidx_a = np.argmin(np.abs(starttime-swarm_a_time))
etidx_a = np.argmin(np.abs(endtime-swarm_a_time))
swarm_a_time = swarm_a_time[stidx_a:etidx_a+1]
swarm_a_utime = swarm_a_time.astype('datetime64[s]').astype(int)

# Identify quality flags (not used in this version, but kept for consistency)
qf_a = v_a.varget('Quality_flags', startrec=stidx_a, endrec=etidx_a)
cf_a = v_a.varget('Calibration_flags', startrec=stidx_a, endrec=etidx_a)

# Read satellite position (Geodetic Coordinates)
swarm_a_glat = v_a.varget('Latitude', startrec=stidx_a, endrec=etidx_a)
swarm_a_glon = v_a.varget('Longitude', startrec=stidx_a, endrec=etidx_a)
r = v_a.varget('Radius', startrec=stidx_a, endrec=etidx_a)
swarm_a_galt = r/1000. - 6371.  # Altitude in km


# Inputs - Swarm C
swarm_c_filename = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/SW_EXPT_EFIC_TCT02_20230227T090151_20230227T120406_0302.cdf'

# Create object to query dataset
v_c = cdflib.CDF(swarm_c_filename)
swarm_c_time = cdflib.epochs.CDFepoch.to_datetime(v_c.varget('Timestamp'))

# Find indices for time range
stidx_c = np.argmin(np.abs(starttime-swarm_c_time))
etidx_c = np.argmin(np.abs(endtime-swarm_c_time))
swarm_c_time = swarm_c_time[stidx_c:etidx_c+1]
swarm_c_utime = swarm_c_time.astype('datetime64[s]').astype(int)

# flags
qf_c = v_c.varget('Quality_flags', startrec=stidx_c, endrec=etidx_c)
cf_c = v_c.varget('Calibration_flags', startrec=stidx_c, endrec=etidx_c)

# Read satellite position (Geodetic Coordinates)
swarm_c_glat = v_c.varget('Latitude', startrec=stidx_c, endrec=etidx_c)
swarm_c_glon = v_c.varget('Longitude', startrec=stidx_c, endrec=etidx_c)
r = v_c.varget('Radius', startrec=stidx_c, endrec=etidx_c)
swarm_c_galt = r/1000. - 6371.  # Altitude in km



# 3D plot to show trajectories
fig_3d = plt.figure(figsize=(12, 12))
ax_3d = fig_3d.add_subplot(111, projection='3d')

# to geodetic
ax_3d.plot(swarm_a_glon, swarm_a_glat, swarm_a_galt, label='Swarm A Trajectory', linewidth=3, color='magenta')
ax_3d.plot(swarm_c_glon, swarm_c_glat, swarm_c_galt, label='Swarm C Trajectory', linewidth=3, color='darkorange')

ax_3d.set_xlabel('Longitude (degrees)')
ax_3d.set_ylabel('Latitude (degrees)')
ax_3d.set_zlabel('Altitude (km)')
ax_3d.set_title('3D Trajectory of Swarm A/C in Geodetic Coordinates')
ax_3d.legend()

plt.show()
