[![codecov](https://codecov.io/gh/mcclaskey/batch_niistats/branch/main/graph/badge.svg)](https://codecov.io/gh/mcclaskey/batch_niistats)

# batch_niistats
Small set of functions that calculate statistics on a batch of 3D nifti files and return the output as a .csv file. Pure python code that works very quickly on all operating systems.

Statistics (mean/standard deviation) can be calculated for all voxels in the .nii, or for only nonzero voxels. This is the equivalent of fslstats with the -M/-S option or -m/-s option, respectively.

# Requirements
* python3.11+

# Instructions

## 1. Create a list of .nii files
Put together a list of your .nii files and save this list as a .csv file where the header row says `input_file` and each subsequent row contains the full path to a .nii file. 

If your files are 4D files and you would like to read a volume other than the first, also include a column called `volume_0basedindex` that specifies which volume to read using 0-based indexing (e.g. use 0 to specify the first volume, 1 for the second, etc). 0-based indexing is used in the style of python, nibabel, FSL, etc. To read multiple volumes/timepoints of a 4D .nii file, list each volume as a separate row in the input datalist.

Alternately, you can specify the volume using SPM-style syntax in the contents of the `input_file` column, as follows: 
```
full\path\to\your.nii,V
```
where V is an integer that indicates the volume number using 1-based indexing, e.g. `path\to\my.nii,1` for the first volume of my.nii. 

Support for SPM syntax is intended to facilitate copying to and from SPM but is otherwise not recommended. If you define filenames in this way, omit single quotations at the start and end of each string that are sometimes retained during SPM copy/paste. `batch_niistats.py` will not strip single quotations from file paths because they could theoretically be part of the file name.

If volumes are specified using both SPM syntax and using a `volume_0basedindex` column, the information in the `volume_0basedindex` column will be preferentially used. If no information is provided, the first volume of each image will be read.

## 2. Run scripts 

Open a terminal (in unix/linux/WSL) or command prompt (in Windows). Activate your project environment and cd to the project directory, then run the following line:
```
batch_niistats [option]
```
where [option] indicates which statistics to calculate for each .nii image, and must be one of: 
- `M`: calculate the mean of nonzero voxels
- `m`: calculate the mean of all voxels
- `S`: calculate the standard deviation of nonzero voxels
- `s`: calculate the standard deviation of all voxels

For example, to calculate mean across only nonzero voxels, type:

```
batch_niistats M
```

The program will start by opening a file selection dialogue box. Select the .csv file you created in step 1 and press ok. Wait while the program runs.

When it is done you will have a .csv file in the same directory as the input .csv file. The output file's name will be be the same as the input file's name but will have a timestamp and the suffix that indicates the option specified as input. 

# Setup 
## Basic Steps
1. create/activate a project environment
2. cd to where you store repos and clone this repo using ```git clone https://github.com/mcclaskey/batch_niistats.git```
3. cd to repo directory
4. run `pip install -e .` to install required packages into your environment

## venv
If you do not have a way to manage environments, here is a quick way to create and activate a python environment for this project:

Create the environment (do this only once):
```
python3 -m venv batch_niistats_env
```

Then to activate the environment: 

On Windows:
```
source batch_niistats_env\Scripts\activate
```

For linux/unix:
```
source batch_niistats_env/bin/activate 
```
