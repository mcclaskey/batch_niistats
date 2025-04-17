#!/usr/bin/env python
# -*- coding : utf-8 -*-

import sys

def batch_niistats(omit_zeros: bool):
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

	import src.modules.utilities as utilities
	import src.modules.nii as nii
	import os
	import pandas as pd
	import datetime
	import concurrent.futures

	##############################################################################
	# start with basic info: ask user for csv, report, check files
	##############################################################################

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
					lambda nii_file: nii.batch_niimean(nii_file, 
													omit_zeros,
													valid_files),
					datalist['input_file'])
					)
			)
		
	##############################################################################
	# create dataframe, show to user, save to csv, end program
	##############################################################################
	combined_df = pd.DataFrame(list_of_data)
	print(combined_df)
	utilities.save_output_csv(combined_df,datalist_filepath)


if __name__ == "__main__":
	if len(sys.argv) < 1:
		omit_zeros = True
	else:
		if sys.argv[1] == "-M":
			omit_zeros = True
		elif sys.argv[1] == "-m":
			omit_zeros = False

	batch_niistats(omit_zeros)