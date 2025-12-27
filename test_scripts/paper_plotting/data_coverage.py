import numpy as np
import matplotlib.pyplot as plt
import pydarn

# Constants
EARTH_RADIUS_KM = 6371  # Approximate Earth radius

# File to read
fitacf_file = "/Users/clevenger/Projects/paper01/sop23_data/202302/08/superdarn/kod/20230208.1000.00.kod.d.fitacf"

# Read file
reader = pydarn.SuperDARNRead(fitacf_file)
fitacf_data = reader.read_fitacf()

# Lists to collect coordinates
lats = []
lons = []

# Loop over records
for rec in fitacf_data:
    try:
        stid = rec['stid']
        beam = rec['bmnum']
        frang = rec.get('frang', 180)
        rsep = rec.get('rsep', 45)
        slist = rec['slist']
        gflg = rec['gflg']
    except KeyError:
        continue

    # Get radar position and beam azimuth
    radar = pydarn.SuperDARNRadars.radars[stid]
    radar_lat = radar.hardware_info.geographic.lat
    radar_lon = radar.hardware_info.geographic.lon
    beam_az_deg = radar.hardware_info.beam_az[beam]  # in degrees

    for j, gate in enumerate(slist):
        if gflg[j] == 0 and gate > 10:
            range_km = frang + gate * rsep
            az_rad = np.radians(beam_az_deg)

            # Estimate offset in lat/lon (flat Earth approximation)
            dlat = (range_km / EARTH_RADIUS_KM) * np.cos(az_rad)
            dlon = (range_km / (EARTH_RADIUS_KM * np.cos(np.radians(radar_lat)))) * np.sin(az_rad)

            lat = radar_lat + np.degrees(dlat)
            lon = radar_lon + np.degrees(dlon)

            lats.append(lat)
            lons.append(lon)

# Plotting
plt.figure(figsize=(10, 6))
plt.scatter(lons, lats, s=3, c='royalblue', alpha=0.7)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("SuperDARN Beam Coverage")
plt.grid(True)
plt.axis("equal")
plt.show()
