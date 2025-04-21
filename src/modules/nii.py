#!/usr/bin/env python
# -*- coding : utf-8 -*-

"""
    Wrapper functions for nii nibabel functions. Add as needed.
    
    Part of batch_niistats package.

	CMcC 4/21/2025 github: https://github.com/mcclaskey/batch_niistats. 
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

def sd_nii(data_array: np.ndarray,
         omit_zeros: bool) -> float:
    """Calculates sd of a data array
    
    """
    if omit_zeros:
        value = data_array[data_array > 0].std()
    else:
        value = data_array.std()
    
    return value

def single_nii_calc(nii_file: list[str],
                            inputs: dict[bool,str],
                            valid_files: list[str]) -> dict[str, float]:
    
    """Calculate statistics for a single .nii file, to be used with map
    
    This function calls the mean/sd functions for a single .nii file and
    returns the output as a dictionary which can be added to a list
    or combined with map().
    
    """
    
	# define label for output var (used as column header)
    if inputs["omit_zeros"]:
        omit_flag = 'nonzero'
    elif inputs["omit_zeros"]:
        omit_flag = 'all'
        
    output_name = f"{inputs["statistic"]} of {omit_flag} voxels"

    # Run calculation only if the file exists
    if nii_file in valid_files:
        nii_array = load_nii(nii_file)

        if inputs["statistic"] == 'mean':
            output_val = mean_nii(nii_array, inputs["omit_zeros"])
        elif inputs["statistic"] == 'sd':
            output_val = sd_nii(nii_array, inputs["omit_zeros"])
            
        return {'filename': nii_file, 
                output_name: output_val}
    else:
        print(f"File not found: {nii_file}")
        return None
    