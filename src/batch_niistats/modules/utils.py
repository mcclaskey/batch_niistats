#!/usr/bin/env python
# -*- coding : utf-8 -*-

"""
    Functions for basic utilities, such as path lookups and reading
    input files.

    Part of batch_niistats package.

    CMcC 4/21/2025 github: https://github.com/mcclaskey/batch_niistats.
"""

import tkinter as tk
from tkinter import filedialog
import pandas as pd
import datetime
import os
import numpy as np


def get_timestamp() -> str:
    """Format the current time as a timestamp and return it as a string"""
    return datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")


def parse_inputs(input_arg: str) -> dict[str, bool | str] | None:
    """Parse user-provided input options

    Reads the user-provided option and defines the statistic
    and whether to use all voxels or only non-zero voxels,
    then returns this as a dict.

    Supported options are:
    M: calculate mean of nonzero voxels
    m: calculate mean of all voxels
    S: calculate standard deviation of nonzero voxels
    s: calculate standard deivation of all voxels
    """

    option_map = {
        "M": {"omit_zeros": True, "statistic": "mean"},
        "m": {"omit_zeros": False, "statistic": "mean"},
        "S": {"omit_zeros": True, "statistic": "sd"},
        "s": {"omit_zeros": False, "statistic": "sd"},
    }

    return option_map.get(input_arg, {})


def askfordatalist() -> str:
    """Prompt user for input CSV file and return full file path as string."""
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename()
    root.destroy()   # Cleanup the Tkinter root window
    return filename


def comma_split(input_spm_path: str) -> dict[str, int | None]:
    """Split SPM-style path at comma, return file and 0-based vol as dict"""
    parts = input_spm_path.split(',')
    if len(parts) > 1 and parts[1].strip().isdigit():
        vol = parts[1].strip()
        volume_index = int(vol) - 1
    else:
        volume_index = None

    return {'file': parts[0], 'volume_spm_0basedindex': volume_index}


def parse_spmsyntax(datalist: pd.DataFrame) -> pd.DataFrame:
    """Handle SPM-style volume syntax in 'input_file' column

    Takes .csv datalist and reads the "input_file" column according to SPM
    syntax for specifying volumes. Returns a dataframe where the input_file
    column is converted to a pure filepath and a new 0-based index column
    containing the SPM volume is added.
    """

    list_of_spmsplit = list(map(comma_split, datalist['input_file']))
    df_of_spmsplits = pd.DataFrame(list_of_spmsplit)

    return pd.concat([datalist, df_of_spmsplits], axis=1)


def prioritize_volume(df):
    """Determine which volume to read for each file given input info

    Reads datalist "df" with potentially multiple volumn columns and resolves
    conflicting or missing values. Determines which volume to read according
    to rules and returns a dataframe with only two columns: 'input_file'
    which has only a pure file path to .nii, and 'volume_0basedindex' column.

    Preference order: explicit volume col > SPM syntax > default to first vol.
    """

    # temp var
    df['volume'] = None

    # uses matching volume
    matches = df['volume_spm_0basedindex'] == df['volume_0basedindex']
    df.loc[matches, 'volume'] = df.loc[matches, 'volume_0basedindex']

    # if conflicts, preferentially read from 'volume_0basedindex'
    user_vol = ~np.isnan(df.loc[~matches, 'volume_0basedindex'])
    df.loc[~matches & user_vol,
           'volume'] = df.loc[~matches & user_vol,
                              'volume_0basedindex']

    # if missingness, read from spm
    missing = df['volume'].isna()
    spm_vol = ~np.isnan(df.loc[missing, 'volume_spm_0basedindex'])
    df.loc[missing & spm_vol,
           'volume'] = df.loc[missing & spm_vol,
                              'volume_spm_0basedindex']

    # if missing, assume first volume
    df.loc[df['volume'].isna(), 'volume'] = 0  # default to first
    df['volume_0basedindex'] = df['volume'].astype(int)
    return df.drop(columns=['volume_spm_0basedindex', 'volume'],
                   errors='ignore')


def load_datalist(datalist_filepath: str) -> pd.DataFrame:
    """Load user-specified input .csv file and return df

    Loads a CSV file containing paths to .nii files and optional volume
    indices.

    Handles SPM-style syntax and fills in missing volume data. Resolves
    conflicting input information and defaults to first volume where
    necessary.

    Returns a dataframe with 'input_file' as pure absolute paths to .nii
    files and 'volume_0basedindex' column with volume indices. Other
    columns in the datalist, if existing, are left unmodified.
    """
    datalist = pd.read_csv(datalist_filepath)

    # now check for SPM volume syntax
    if datalist['input_file'].astype(str).str.contains(',').any():
        datalist = parse_spmsyntax(datalist)
    else:
        datalist['file'] = datalist['input_file']
        datalist['volume_spm_0basedindex'] = np.nan

    if 'volume_0basedindex' not in datalist.columns:
        datalist['volume_0basedindex'] = np.nan

    return prioritize_volume(datalist)


def create_output_df(datalist: pd.DataFrame,
                     list_of_data: list) -> pd.DataFrame:
    """Merges input and output df and returns df with original index order"""
    calculated_df = pd.DataFrame(list_of_data)
    calculated_df['input_file'] = calculated_df['input_file'].str.strip()
    calculated_df = calculated_df.reset_index()

    input_df = datalist.drop(columns=["volume_0basedindex", "file"],
                             axis=1,
                             errors='ignore')
    input_df = input_df.reset_index()
    input_df['input_file'] = input_df['input_file'].str.strip()

    combined_df = input_df.merge(calculated_df,
                                 on=['input_file', 'index'],
                                 how='outer',
                                 sort=False)
    combined_df = combined_df.sort_values(by='index')
    combined_df = combined_df.drop(columns=["index"], axis=1)
    combined_df = combined_df.reset_index(drop=True)

    return combined_df


def write_output_df_path(datalist_filepath: str,
                         statistic: str,
                         timestamp: str) -> str:
    """Create name and full filepath for output .csv

    Output file will be in the same directory as input .csv.
    File name includes the timestamp and statistic.
    """

    timestamp_dt = datetime.datetime.strptime(timestamp, "%Y.%m.%d %H:%M:%S")
    timestamp_file = timestamp_dt.strftime("%Y%m%d_%H%M%S")

    output_dir = os.path.dirname(datalist_filepath)
    base_name = os.path.basename(datalist_filepath)
    base_name = base_name.replace('.csv', f'_calc_{statistic}.csv')
    output_path = os.path.join(output_dir, f"{timestamp_file}_{base_name}")

    return output_path


def save_output_csv(output_df: pd.DataFrame,
                    output_path: str):
    """Saves output csv to file path"""
    output_df.to_csv(output_path, index=False)
    print(f"\nOutput saved to file:\n{output_path}\n")
