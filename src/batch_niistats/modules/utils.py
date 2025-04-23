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
  return filedialog.askopenfilename()


def comma_split(input_spm_path: str) -> dict[str, int | None]:
	"""Split SPM-style path at comma, return file and 0-based vol as dict"""
	parts = input_spm_path.split(',')
	if len(parts) == 1:
		volume_index  = None
	else:
		volume_index  = int(parts[1]) - 1

	return {'input_file': parts[0],'volume_spm_0basedindex': volume_index }

def parse_spmsyntax(datalist: pd.DataFrame) -> pd.DataFrame:
	"""Handle SPM-style volume syntax in 'input_file' column

    Takes .csv datalist and reads the "input_file" column according to SPM
	syntax for specifying volumes. Returns a dataframe where the input_file
	column is converted to a pure filepath and a new 0-based index column
	containing the SPM volume is added.
    """

	list_of_spmsplit = list(map(comma_split,datalist['input_file']))
	df_of_spmsplits = pd.DataFrame(list_of_spmsplit)

	other_cols = datalist.drop(columns=['input_file'], errors='ignore')
	return pd.concat([df_of_spmsplits, other_cols], axis=1)

def prioritize_volume(datalist):
	"""Determine which volume to read for each file given input info
	
	Reads datalist with potentially multiple volumn columns and resolves 
	conflicting or missing values. Determines which volume to read according
	to rules and returns a dataframe with only two columns: 'input_file' which
	has only a pure file path to .nii, and 'volume_0basedindex' column.

    Preference order: explicit volume col > SPM syntax > default to first vol.
    """
	
	# temp var
	datalist['volume'] = None	
	
	# uses matching volume
	matches = datalist['volume_spm_0basedindex'] == datalist['volume_0basedindex']
	datalist.loc[matches,'volume'] = datalist.loc[matches,'volume_0basedindex']

	# if conflicts, preferentially read from user created column 'volume_0basedindex'
	user_vol = ~np.isnan(datalist.loc[~matches, 'volume_0basedindex'])
	datalist.loc[~matches & user_vol, 'volume'] = datalist.loc[~matches & user_vol, 'volume_0basedindex']

	# otherwise read from spm
	spm_vol = ~np.isnan(datalist.loc[~matches,'volume_spm_0basedindex'])
	datalist.loc[~matches & spm_vol ,'volume'] = datalist.loc[~matches & spm_vol ,'volume_spm_0basedindex']

	# if missing, assume first volume
	datalist.loc[datalist['volume'].isna(), 'volume'] = 0  # default to first volume
	datalist['volume_0basedindex'] = datalist['volume'].astype(int)
	return datalist.drop(columns=['volume_spm_0basedindex', 'volume'], errors='ignore')


def load_datalist(datalist_filepath: str) -> pd.DataFrame:
	"""Load user-specified input .csv file and return formatting dataframe
	
	Loads a CSV file containing paths to .nii files and optional volume indices.

    Handles SPM-style syntax and fills in missing volume data. Resolves conflicting
	input information and defaults to first volume where necessary. 

	Returns a dataframe with 'input_file' as pure absolute paths to .nii files 
	and 'volume_0basedindex' column with volume indices. Other columns in the
	datalist, if existing, are left unmodified.
    """
	datalist = pd.read_csv(datalist_filepath)

	# now check for SPM volume syntax
	if datalist['input_file'].astype(str).str.contains(',').any():
		datalist = parse_spmsyntax(datalist)
	else:
		datalist['volume_spm_0basedindex'] = None

	if 'volume_0basedindex' not in datalist.columns:
		datalist['volume_0basedindex'] = None

	return prioritize_volume(datalist)

def report_usage() -> str:
	"""Print usage information to the terminal."""
	usage_text = (
		"\nUsage: python batch_niistats.py [option]\n\n"
		"Options:\n\n"
		"M: output mean (for nonzero voxels only)\n"
		"m: output mean (for all voxels in image)\n"
		"S: output standard deviation (for nonzero voxels only)\n"
		"s: output standard deviation (for all voxels)\n\n"
		"You will then be prompted for a list of .nii files to process.\n\n"
		"This list must be a CSV file with columns 'input_file' and\n"
		"'volume_0basedindexing'.\n\n"
		"'input_file' lists the absolute paths to each .nii file and\n"
		"'volume_0basedindexing' indicates the volume to read, using\n"
		"0-based indexing (e.g. use 0 to specify the first volume and 1\n"
		"for the second, etc).\n\n"
		"In lieu of a 'volume_0basedindex' column, volumes can also be\n"
		"specified in the input_file column using SPM syntax where ',N' is\n"
		"placed after the filename. N indicates volume using 1-based indexing.\n\n"
		"The 'volume_0basedindexing' column or SPM synax can be omitted if\n"
		"all files are 3D NIfTIs or if you only want to calculate statistics\n"
		"on the first volume of each image.\n\n"
		)
	
	print(usage_text.format())

def save_output_csv(output_df: pd.DataFrame, 
					datalist_filepath: str,
					statistic: str,
					timestamp: str):
	"""Save data to output .csv in the same directory as input .csv

    File name includes the timestamp and statistic.
    """
	
	timestamp_dt = datetime.datetime.strptime(timestamp,"%Y.%m.%d %H:%M:%S")
	timestamp_file = timestamp_dt.strftime("%Y%m%d_%H%M%S")
	statistic_clean = statistic.replace('-', '')

	output_dir = os.path.dirname(datalist_filepath)
	base_name = os.path.basename(datalist_filepath).replace('.csv', f'_calc_{statistic_clean}.csv')
	output_path = os.path.join(output_dir, f"{timestamp_file}_{base_name}")

	output_df.to_csv(output_path, index=False)
	print(f"\nOutput saved to file:\n{output_path}\n")
