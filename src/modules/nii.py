#!/usr/bin/env python
# -*- coding : utf-8 -*-

"""
    Wrapper functions for nii nibabel functions. Add as needed.
"""

import nibabel as nb
import numpy as np

def load_nii(input_file: str) -> np.ndarray:

    """ Call nibabel to load first volumn of .nii file

    We can't assume that array is 2D, so load to array and check. 
    Returns a 3-D array.

    """
    img_proxy = nb.load(input_file)
    data_array = np.asarray(img_proxy.get_fdata())
    if data_array.ndim == 4:
        data_array = data_array[...,0] #get only first volume
    
    return(data_array)

def mean_nii(data_array: np.ndarray,
         omit_zeros: bool) -> float:
    """Calculates mean of a data array
    
    """
    if omit_zeros:
        value = data_array[data_array > 0].mean()
    else:
        value = data_array.mean()
    
    return value

def batch_niimean(nii_file: list[str],
                            omit_zeros: bool,
                            valid_files: list[str]) -> dict[str, float]:
    
    """Calls nibabel_mean for a single file, to be used with map
    
    This function calls mean_omitzeroes for a single .nii file and
    returns the output as a dictionary which can be added to a list
    or combined with map().
    
    """
    if omit_zeros:
        omit_flag = 'mean of nonzero voxels'
    else:
        omit_flag = 'mean of all voxels'

    # Call mean() only if the file exists
    if nii_file in valid_files:
        nii_array = load_nii(nii_file)
        return {'filename': nii_file, 
                omit_flag: mean_nii(nii_array, omit_zeros)}
    else:
        print(f"File not found: {nii_file}")
        return None
    