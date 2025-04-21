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