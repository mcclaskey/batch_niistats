#!/usr/bin/env python
# -*- coding : utf-8 -*-

import argparse
from batch_niistats import nii, utils
import os
import pandas as pd
import concurrent.futures


def main():
	"""Calculate statistics for batch of .nii files and save .csv of output

	Function to calculate statistics for a set of nifti iamges and save a 
	.csv file with the output. Which statistic to be calculated, and 
	whether all voxels or only nonzero voxels are included, is specified
	via input args. Supported inputs are -S, -s, -M, -m and follow FSL's
	conventions for input options.

	This function prompts the user for the csv file that contains input 
	.nii files (which was used in the bash script), and then compiles the 
	output into a csv file. 

	For details & issues, see https://github.com/mcclaskey/batch_niistats.

	CMcC 4.9.2025
	"""

	##########################################################################
	# handle input arguments
	##########################################################################
	parser = argparse.ArgumentParser(
        description="Calculate statistics from a list of .nii files."
    )
	parser.add_argument(
        "option",
        choices=["-M", "-m", "-S", "-s"],
        help="Statistical option: -M (mean, nonzero), -m (mean, all), "
             "-S (sd, nonzero), -s (sd, all)"
    )

	args = parser.parse_args()

	##########################################################################
	# start with basic info: ask user for csv, report, check files
	##########################################################################

	# parse inputs
	inputs = utils.parse_inputs(args.option)
	if not inputs:
		utils.report_usage()
		return

	# ask for datalist (csv, first row must be "input_file")
	datalist_filepath = utils.askfordatalist()

	# print info for user reference
	timestamp = utils.get_timestamp()
	print(f"[{timestamp}] batch_niistats.py\n\nCompiling .csv file with "
		f"{inputs["statistic"]} values of .nii files listed in:\n"
		f"{datalist_filepath}\n")

	# read it and check for missing files
	datalist = utils.load_datalist(datalist_filepath)
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
	utils.save_output_csv(combined_df,
							datalist_filepath,
							args.option,
							timestamp)


if __name__ == "__main__":
	main()