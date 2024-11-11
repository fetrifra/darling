"""Collection of pre-implemneted h5 readers developed for id03 format.

NOTE: In general the file reader is strongly dependent on data collection scheme and it is therefore the
purpose of darling to allow the user to subclass Reader() and implement their own specific data structure.

Once the reader is implemented in darling format it is possible to interface the DataSet class and use
all features of darling.

"""

import h5py
import hdf5plugin
import matplotlib.pyplot as plt
import numpy as np


class Reader(object):
    """Parent class for readers.

    Attributes:
        abs_path_to_h5_file (:obj: `str`): Absolute file path to data.

    """

    def __init__(self, abs_path_to_h5_file):
        self.abs_path_to_h5_file = abs_path_to_h5_file

    def read_scan(self, args, scan_id, roi=None):
        """Method to read a single 2D scan

        NOTE: This method is meant to be purpose implemented to fit the specific data aqusition
            scheme used.

        Args:
            args str (:obj:`list`): list of arguments needed by the reader.
            scan_id (:obj:`str`): scan id to load from, these are internal kayes to diffirentiate
                layers.
            roi (:obj:`tuple` of :obj:`int`): row_min row_max and column_min and column_max, 
                defaults to None, in which case all data is loaded. The roi refers to the detector
                dimensions.

        Returns:
            data (:obj:`numpy array`) of shape=(a,b,m,n) and type np.uint16 and motors 
            (:obj:`tuple` of :obj:`numpy array`) of shape=(m,) and shape=(n,) and type
            np.float32. a,b are detector dimensions while m,n are scan dimensions over 
            which teh motor settings vary.

        """
        pass


class MosaScan(Reader):
    """Load a 2D mosa scan.

    Args:
        abs_path_to_h5_file str (:obj:`str`): absolute path to the h5 file with the diffraction images.
        motor_names data (:obj:`list` of :obj:`str`): h5 paths to the data [chi, phi, strain] these need to be ordered
            to match the scan sequence.
        motor_precision data (:obj:`list` of :obj:`int`): number of trusted deciamls in each motor dimension. (matching motor_names)
    """

    def __init__(
        self,
        abs_path_to_h5_file,
        motor_names,
        motor_precision,
    ):
        self.abs_path_to_h5_file = abs_path_to_h5_file
        self.motornames = motor_names
        self.motor_precision = motor_precision

        assert len(self.motor_precision) == len(
            self.motornames
        ), "The motor_precision lengths need to match the motornames length"

    def read_scan(self, data_name, scan_id, roi=None):
        """Load a scan

        this loads the mosa data array with shape N,N,m,n where N is the detector dimension and
        m,n are the motor dimensions as ordered in the self.motor_names.

        Args:
            data_name (:obj:`str`): path to the data wihtout the prepended scan id
            scan_id (:obj:`str`):scan id to load from, e.g 1.1, 2.1 etc...
            roi (:obj:`tuple` of :obj:`int`): row_min row_max and column_min and column_max, 
                defaults to None, in which case all data is loaded

        Returns:
            data, motors : data of shape (a,b,m,n) and motors tuple of len=m and len=n

        """
        with h5py.File(self.abs_path_to_h5_file, "r") as h5f:
            # Read in motors
            raw_motors = [h5f[scan_id][mn] for mn in self.motornames]
            motors = [
                np.unique(np.round(m, p)).astype(np.float32)
                for p, m in zip(self.motor_precision, raw_motors)
            ]
            voxel_distribution_shape = [len(m) for m in motors]

            # read in data and reshape
            if roi:
                r1, r2, c1, c2 = roi
                data = h5f[scan_id][data_name][:, r1:r2, c1:c2]
            else:
                data = h5f[scan_id][data_name][:, :, :]

            data = data.reshape(
                (*voxel_distribution_shape, data.shape[-2], data.shape[-1])
            )
            data = data.swapaxes(0, 2)
            data = data.swapaxes(1, -1)
        
        return data, motors

# TODO: implement the strain scan reader.
# TODO: test these classe with h5 files from id03.

if __name__ == "__main__":
    pass