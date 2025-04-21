#!/usr/bin/env python
# -*- coding : utf-8 -*-

import sys
import src.modules.utilities as utilities

def batch_niistats(input_arg: str):
	"""
	Function to calculate the mean value of a set of .nii and returns a .csv
	file with the output values. The mean value of each .nii is calculated
	across all nonzero voxels in the image.

	This function prompts the user for the csv file that contains input 
	.nii files (which was used in the bash script), and then compiles the 
	output into a csv file. 

	For details & issues, see https://github.com/mcclaskey/batch_niistats.

	CMcC 4.9.2025
	"""

	##############################################################################
	#Import modules, packages, and the datalist
	##############################################################################

	import src.modules.nii as nii
	import os
	import pandas as pd
	import datetime
	import concurrent.futures

	##############################################################################
	# start with basic info: ask user for csv, report, check files
	##############################################################################
	# parse inputs
	inputs = utilities.parse_inputs(input_arg)

	# ask for datalist (csv, first row must be "input_file")
	datalist_filepath = utilities.askfordatalist()

	# print info for user reference
	timestamp_here = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
	print(f"[{timestamp_here}] batch_niistats.py.\n\nCompiling .csv file with "
		f"mean values of .nii files listed in:\n{datalist_filepath}")

	# read it and check for missing files
	datalist = pd.read_csv(datalist_filepath)
	valid_files = {f for f in datalist['input_file'] if os.path.exists(f)}

	##############################################################################
	# Loop through the rows in the csv, call batch_niimean and add result to list
	##############################################################################
	with concurrent.futures.ThreadPoolExecutor() as executor:
		list_of_data = list(
			filter(
				None, 
				executor.map(
					lambda nii_file: nii.single_nii_calc(nii_file, 
													inputs,
													valid_files),
					datalist['input_file'])
					)
			)
		
	##############################################################################
	# create dataframe, show to user, save to csv, end program
	##############################################################################
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