#!/usr/bin/env python
# -*- coding : utf-8 -*-

import argparse
from batch_niistats.modules import nii, utils
import os
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
        description=(
            "Calculate descriptive statistics on a list of 3D .nii files\n"
            "and return the result as a csv file.\n\n"
            "Specify which statistic to calculate using the 1st positional\n"
            "argument, which must be one of the following:\n"
            "  M: calculate mean of non-zero voxels in image\n"
            "  m: calculate mean of all voxels in image\n"
            "  S: calculate standard deviation of non-zero voxels in image\n"
            "  s: calculate standard deviation of all voxels in image\n\n"
            "Example: batch_niistats M\n\n"
            "Once the program starts, you will prompted for a list of .nii\n"
            "files to process. This list must be a CSV file with columns\n"
            "'input_file' and (optionally) 'volume_0basedindex'. Row 1 must\n"
            "contain column headers.\n\n"
            "The 'input_file' column must contain the absolute paths to each"
            "\n.nii. If your files are 4D files and you would like to read a"
            "\nvolume other than the 1st, use the optional "
            "'volume_0basedindex'\ncolumn to specify which volume to read "
            "using 0-based indexing\n(e.g. use 0 to specify the first "
            "volume, 1 for the second, etc).\nTo read multiple volumes/"
            "timepoints of a 4D .nii file, list each\nvolume as a separate "
            "row in the input .csv file.\n\n"
            "In lieu of a 'volume_0basedindex' column, volumes can also be\n"
            "specified in the input_file column using SPM syntax where ',V' "
            "is\nplaced after the filename, e.g. ''path/to/my/file.nii,V'' "
            "and\nindicates volume using 1-based indexing. For example,\n"
            "''path/to/my/file.nii,1'' reads the first volume of file.nii."
            "\n\nSupport for SPM syntax is intended to facilitate copying to "
            "and\nfrom SPM but is otherwise not recommended. If you define\n"
            "filenames in this way, omit single quotations at the start and\n"
            "end of each string that are sometimes retained during SPM\n"
            "copy/paste.\n\nThe 'volume_0basedindex' column or the SPM synax"
            " can be omitted\nif all files are 3D NIfTIs or if you only want "
            "to calculate\nstatistics on the first volume of each image.\n\n"
            ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "option",
        choices=["M", "m", "S", "s"],
        help="Statistic to calculate:\n"
         "  M: mean of nonzero voxels\n"
         "  m: mean of all voxels\n"
         "  S: stddev of nonzero voxels\n"
         "  s: stddev of all voxels")

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
    print(
        f"[{timestamp}] batch_niistats.py\n\nCompiling .csv file with "
        f"{inputs['statistic']} values of .nii files listed in:\n"
        f"{datalist_filepath}\n"
        )

    # read it and check for missing files
    datalist = utils.load_datalist(datalist_filepath)
    valid_files = {f for f in datalist['file'] if os.path.exists(f)}

    ##########################################################################
    # Loop across rows in csv, call single_nii_calc, add result to list
    ##########################################################################
    with concurrent.futures.ThreadPoolExecutor() as executor:
        single_nii_results = executor.map(
            lambda args: nii.try_single_nii_calc(args[0],
                                                 args[1],
                                                 args[2],
                                                 inputs,
                                                 valid_files),
            zip(datalist['input_file'],
                datalist['file'],
                datalist['volume_0basedindex'])
            )
        list_of_data = list(single_nii_results)

    ##########################################################################
    # create dataframe, show to user, save to csv, end program
    ##########################################################################
    output_path = utils.write_output_df_path(
        datalist_filepath,
        args.option,
        timestamp)
    combined_df = utils.create_output_df(datalist, list_of_data)
    utils.save_output_csv(combined_df, output_path)

    return combined_df


if __name__ == "__main__":  # pragma: no cover
    main()
