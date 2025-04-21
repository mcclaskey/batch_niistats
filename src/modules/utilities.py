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

def get_timestamp(*args) -> str:
	"""Gets a timestamp at the start, which is used for labeling and reporting
	
	"""
	return datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")

def parse_inputs(input_arg: str) -> dict[bool,str]:
	"""Parses user-provided input option
	
	Reads the user-provided option and defines the statistic
	and whether to use all voxels or only non-zero voxels, 
	then returns this as a dict
	"""
	if input_arg == "-M":
		inputs = {'omit_zeros': True, 'statistic': 'mean'}
	elif input_arg == "-m":
		inputs = {'omit_zeros': False, 'statistic': 'mean'}
	elif input_arg == "-S":
		inputs = {'omit_zeros': True, 'statistic': 'sd'}
	elif input_arg == "-s":
		inputs = {'omit_zeros': False, 'statistic': 'sd'}

	return(inputs)


def askfordatalist(*args) -> str:
  """Asks user for data list file

  first row must say "input_file" and rest must be list of files

  """
  root = tk.Tk()
  root.withdraw()
  datalist_filepath = filedialog.askopenfilename()
  return datalist_filepath
def comma_split(input_spm_path: str) -> Dict[str, Optional[int]]:
	"""Splits a path by comma (SPM-style) and extracts the volume index (0-based).
	
	"""
	parts = input_spm_path.split(',')
	if len(parts) == 1:
		volume_index  = None
	else:
		volume_index  = int(parts[1]) - 1

	return {'input_file': parts[0],'volume_spm_0basedindex': volume_index }

def parse_spmsyntax(datalist: pd.DataFrame) -> pd.DataFrame:
	"""
	Handles SPM-style volume syntax in 'input_file' column.

    Splits the filename and extracts volume, then merges with original DataFrame.
    """

	list_of_spmsplit = list(map(comma_split,datalist['input_file']))
	df_of_spmsplits = pd.DataFrame(list_of_spmsplit)

	other_cols = datalist.drop(columns=['input_file'], errors='ignore')
	return pd.concat([df_of_spmsplits, other_cols], axis=1)

def prioritize_volume(datalist):
	"""
    Resolves the volume to load when there are conflicting or missing values.

    Preference order: explicit volume column > SPM syntax > default to volume 1.
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

	"""
    Loads a CSV file containing paths to .nii files and optional volume indices.

    Handles SPM-style syntax and fills in missing volume data.
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

def report_usage(*args) -> str:
   """ Defines the text used to repor usage to the user
   
   """
   usage_text = ("\nUsage: python batch_niistats.py [option]\n\n"
				"Options:\n\n-M: output mean (for nonzero voxels only)\n"
				"-m: output mean (for all voxels in image)\n\nYou will then "
				"be prompted for a list of .nii files to process.\nThis list "
				"must be a single-column csv file where the first row\nsays "
				"'input_file' and the subsequent rows are absolute paths\nto "
				"each file.")
   print(usage_text.format())

def save_output_csv(output_df: pd.DataFrame, 
                    datalist_filepath: str,
                    statistic: str,
					timestamp: str):
    
    """Saves data to csv file in same directory as input, with 
    timestamp
    
    """
	
	# format statistic and timestamp for output file
    timestamp_dt = datetime.datetime.strptime(timestamp,"%Y.%m.%d %H:%M:%S")
    timestamp_file = timestamp_dt.strftime("%Y%m%d_%H%M%S")
    statistic = statistic.replace('-','')

    # get output dir
    output_dir = os.path.dirname(datalist_filepath)
    
	# get output filename
    datalist_fname = os.path.basename(datalist_filepath)
    datalist_fname = datalist_fname.replace('.csv',f'_calc_{statistic}.csv')
    output_fname = f"{timestamp_file}_{datalist_fname}"
    
	# save to file
    output_csv_fullfile = os.path.join(output_dir,output_fname)
    output_df.to_csv(output_csv_fullfile, index=False)
    print(f"\nOutput saved to file:\n{output_csv_fullfile}\n")