#!/usr/bin/env python
# -*- coding : utf-8 -*-

import argparse
from batch_niistats.modules import nii, utils
import os
import pandas as pd
import concurrent.futures


def main():
	"""Calculate statistics for batch of .nii files and save .csv of output

	Function to calculate statistics for a set of nifti iamges and save a 
	.csv file with the output. Which statistic to be calculated, and 
	whether all voxels or only nonzero voxels are included, is specified
	via input args. Supported inputs are S, s, M, m and follow FSL's
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
        description=(f"Calculate statistics from a list of .nii files.\n\n"
		f"Once the program starts, you will prompted for a list of .nii\n"
		f"files to process. This list must be a CSV file with columns\n"
		f"'input_file' and (optionally) 'volume_0basedindexing'.\n\n"
		f"'input_file' lists the absolute paths to each .nii file and\n"
		f"'volume_0basedindexing' indicates the volume to read, using\n"
		f"0-based indexing (e.g. use 0 to specify the first volume and 1\n"
		f"for the second, etc).\n\n"
		f"In lieu of a 'volume_0basedindex' column, volumes can also be\n"
		f"specified in the input_file column using SPM syntax where ',N' is\n"
		f"placed after the filename. N indicates volume using 1-based indexing.\n\n"
		f"The 'volume_0basedindexing' column or SPM synax can be omitted if\n"
		f"all files are 3D NIfTIs or if you only want to calculate statistics\n"
		f"on the first volume of each image.\n\n"),
		formatter_class=argparse.RawDescriptionHelpFormatter,
    )
	parser.add_argument(
        "option",
        choices=["M", "m", "S", "s"],
        help="Statistical option: M (mean, nonzero), m (mean, all), "
             "S (sd, nonzero), s (sd, all)"
    )

	args = parser.parse_args()

	##########################################################################
	# start with basic info: ask user for csv, report, check files
	##########################################################################

	# parse inputs
	inputs = utils.parse_inputs(args.option)

	# ask for datalist (csv, first row must be "input_file")
	datalist_filepath = utils.askfordatalist()

	# print info for user reference
	timestamp = utils.get_timestamp()
	print(f"[{timestamp}] batch_niistats.py\n\nCompiling .csv file with "
		f"{inputs["statistic"]} values of .nii files listed in:\n"
		f"{datalist_filepath}\n")

	# read it and check for missing files
	datalist = utils.load_datalist(datalist_filepath)
	valid_files = {f for f in datalist['file'] if os.path.exists(f)}

	##########################################################################
	# Loop across rows in csv, call single_nii_calc, add result to list
	##########################################################################
	with concurrent.futures.ThreadPoolExecutor() as executor:
		single_nii_results = executor.map(
			lambda args: nii.try_single_nii_calc(args[0],args[1],args[2],inputs,valid_files),
			zip(datalist['input_file'],datalist['file'],datalist['volume_0basedindex'])
			)
		list_of_data = list(single_nii_results)
	
	##########################################################################
	# create dataframe, show to user, save to csv, end program
	##########################################################################
	combined_df = utils.create_output_df(datalist,list_of_data)
	utils.save_output_csv(combined_df,
							datalist_filepath,
							args.option,
							timestamp)
	
	return(combined_df)

if __name__ == "__main__":
	main()