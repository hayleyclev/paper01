import h5py
import scipy.io

def print_mat_contents(asifn):
    mat = scipy.io.loadmat(asifn, struct_as_record=False, squeeze_me=True)
    print(f"File: {asifn}")
    for key in mat:
        if not key.startswith('__'):
            print(f"Variable: {key}")
            print(f"  Type: {type(mat[key])}")
            try:
                print(f"  Shape: {mat[key].shape}")
            except AttributeError:
                print(f"  Value: {mat[key]}")
            print()
            
asifn = '/Users/clevenger/Projects/paper01/sop23_data/202302/27/asi/crossing1/in/skymap.mat'