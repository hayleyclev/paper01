import h5py
import numpy as np

filename_lp = '/Users/clevenger/Projects/paper01/sop23_data/202303/31/20230331.001_lp_5min-fitcal.h5'

with h5py.File(filename_lp, 'r') as h5:
    beamcodes = h5['BeamCodes'][:]
    
    # Get all unique beamcodes
    unique_beamcodes = np.unique(beamcodes[:, 0])
    
    # Dictionary to store data for each beamcode
    beamcode_data = {}
    
    print(beamcodes)
