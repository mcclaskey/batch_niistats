#!/usr/bin/env python
# -*- coding : utf-8 -*-

import sys
import src.modules.utilities as utilities

def batch_niistats(input_arg: str):
	"""Calculates statistics for batch of .nii files and saves .csv of output

	Function to calculate statistics for a set of nifti iamges and save a 
	.csv file with the output. Which statistic to be calculated, and 
	whether all voxels or only nonzero voxels are included, is specified
	via input_arg. Supported inputs are -S, -s, -M, -m and follow FSL's
	conventions for input options.

	This function prompts the user for the csv file that contains input 
	.nii files (which was used in the bash script), and then compiles the 
	output into a csv file. 

	For details & issues, see https://github.com/mcclaskey/batch_niistats.

	CMcC 4.9.2025
	"""

	##########################################################################
	# Import modules, packages, and the datalist
	##########################################################################

	import src.modules.nii as nii
	import os
	import pandas as pd
	import concurrent.futures

	##########################################################################
	# start with basic info: ask user for csv, report, check files
	##########################################################################

	# parse inputs
	inputs = utilities.parse_inputs(input_arg)

	# ask for datalist (csv, first row must be "input_file")
	datalist_filepath = utilities.askfordatalist()

	# print info for user reference
	timestamp = utilities.get_timestamp()
	print(f"[{timestamp}] batch_niistats.py\n\nCompiling .csv file with "
		f"{inputs["statistic"]} values of .nii files listed in:\n"
		f"{datalist_filepath}\n")

	# read it and check for missing files
	datalist = utilities.load_datalist(datalist_filepath)
	valid_files = {f for f in datalist['input_file'] if os.path.exists(f)}

	##########################################################################
	# Loop across rows in csv, call single_nii_calc, add result to list
	##########################################################################
	with concurrent.futures.ThreadPoolExecutor() as executor:
		single_nii_results = executor.map(
			lambda args: nii.try_single_nii_calc(args[0],args[1],inputs,valid_files),
			zip(datalist['input_file'],datalist['volume_0basedindex'])
			)
		list_of_data = list(single_nii_results)
		
	##########################################################################
	# create dataframe, show to user, save to csv, end program
	##########################################################################
	combined_df = pd.DataFrame(list_of_data)
	print(combined_df)
	utilities.save_output_csv(combined_df,
							datalist_filepath,
							input_arg,
							timestamp)


if __name__ == "__main__":
	supported_inputs = ["-M","-m","-S","-s"]
	
	if len(sys.argv) == 1:
		utilities.report_usage()
	else:
		if sys.argv[1] in supported_inputs:
			batch_niistats(sys.argv[1])
		else:
			utilities.report_usage()