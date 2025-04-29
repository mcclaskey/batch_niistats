#!/usr/bin/env python
# -*- coding : utf-8 -*-

"""
    Functions that manipulate or handle .nii files. Coded using nibabel.

    Part of batch_niistats package.

    CMcC 4/21/2025 github: https://github.com/mcclaskey/batch_niistats.
"""

import nibabel as nb
import numpy as np


def load_nii(
        input_file: str,
        nii_volume: int
        ) -> np.ndarray:
    """Use nibabel to load a volume of .nii file, returns 3D NumPy array."""
    img_proxy = nb.load(input_file)
    data_array = np.asarray(img_proxy.get_fdata())

    if data_array.ndim == 4:
        data_array = data_array[..., nii_volume]  # get only first volume

    return data_array


def mean_nii(
        nii_array: np.ndarray,
        omit_zeros: bool
        ) -> float:
    """Calculate mean of a 3D NumPy array, return single number

    If omit_zeros is True, only nonzero voxels are included in calculation.
    """

    return nii_array[nii_array > 0].mean() if omit_zeros else nii_array.mean()


def sd_nii(
        data_array: np.ndarray,
        omit_zeros: bool
        ) -> float:
    """Calculate the standard deviation of a 3D NumPy array, return float

    If omit_zeros is True, only nonzero voxels are included in sd calculation.
    """

    return data_array[data_array > 0].std() if omit_zeros else data_array.std()


def try_single_nii_calc(nii_rawinput: str,
                        nii_file: str,
                        nii_volume: int,
                        inputs: dict[str, bool | str],
                        valid_files: set[str]
                        ) -> dict[str, str | int | float] | None:
    """Safely call single_nii_calc with error handling.

    Returns None if there is an exception. Returns dictionary otherwise.
    """
    try:
        return single_nii_calc(
            nii_rawinput,
            nii_file,
            nii_volume,
            inputs,
            valid_files
            )
    except Exception as e:
        print(f"Error processing {nii_file}: {e}")
        return None


def single_nii_calc(nii_rawinput: str,
                    nii_file: str,
                    nii_volume: str,
                    inputs: dict[str, bool | str],
                    valid_files: set[str]
                    ) -> dict[str, str | int | float]:
    """Calculate statistics for a single .nii file, to be used with map

    This function calls the mean/sd functions for a single .nii file and
    returns the output as a dictionary to be converted to pandas data frame.
    """

    # define label for output var (used as column header)
    if inputs['omit_zeros']:
        omit_flag = 'nonzero'
    elif not inputs['omit_zeros']:
        omit_flag = 'all'

    # Run calculation only if the file exists
    if nii_file in valid_files:
        nii_array = load_nii(nii_file, nii_volume)
        filestatus = 'file exists'

        if inputs['statistic'] == 'mean':
            output_val = mean_nii(nii_array, inputs["omit_zeros"])
        elif inputs['statistic'] == 'sd':
            output_val = sd_nii(nii_array, inputs["omit_zeros"])
    else:
        print(f"File not found: {nii_file}")
        filestatus = 'file not found'
        output_val = None

    return {'input_file': nii_rawinput,
            'filename': nii_file,
            'volume_0basedindex': nii_volume,
            f"{inputs['statistic']} of {omit_flag} voxels": output_val,
            'note': filestatus}
