# batch_niistats: calculate stats on a batch of .nii files
![Python Versions](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-blue) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![batch_niistats-tests](https://img.shields.io/github/actions/workflow/status/mcclaskey/batch_niistats/python-package.yml?label=batch_niistats-tests&logo=github)](https://github.com/mcclaskey/batch_niistats/actions/workflows/python-package.yml)
 [![codecov](https://codecov.io/gh/mcclaskey/batch_niistats/branch/main/graph/badge.svg)](https://codecov.io/gh/mcclaskey/batch_niistats)


Calculate statistics on a batch of 3D NIfTI files and return the output as a `.csv` file. 

Statistics (mean/standard deviation) can be calculated for all voxels in the nifti, or for only nonzero voxels. This equivalent to using FSL's `fslstats` with the `-M`/`-S` option or `-m`/`-s` option, respectively.

# Requirements
* python3.11+

# Instructions

### 1. Create a list of NIfTI files
Put together a list of your NIfTI files and save this list as a .csv file where the header row says `input_file` and each subsequent row contains the full path to a NIfTI file. `batch_niistats` can read both zipped (.nii.gz) and unzipped (.nii) NIfTI files.

If you have 4D files and you would like to read a volume other than the first, also include a column called `volume_0basedindex` that specifies which volume to read using **0-based indexing** (_e.g._ `0` for the first volume, `1` for the second, etc). 0-based indexing matches the conventions of python, NiBabel, FSL, etc. To read multiple volumes of the same 4D nifti file, list each volume as a separate row in the input `.csv` file.

Alternatively, you can specify the volume using SPM-style syntax in the `input_file` column, as follows: 
```
full\path\to\your.nii,V
```
where V is an integer that indicates the volume number using **1-based indexing**, _e.g._ `path\to\my.nii,1` for the first volume of my.nii. 

Support for SPM syntax is intended to facilitate copying to and from SPM but is otherwise not recommended. If you define filenames in this way, omit single quotations at the start and end of each string that are sometimes retained during SPM copy/paste. `batch_niistats` does not strip single quotations from file paths because they could be valid characters in some filenames.

If volumes are specified using both SPM syntax and using a `volume_0basedindex` column, the information in the `volume_0basedindex` column will be preferentially used. If no information is provided, `batch_niistats` will read the first volume of each image by default.

### 2. Call `batch_niistats` 

Open a terminal (in Unix/Linux/WSL) or command prompt (in Windows), activate your virtual environment (if necessary), then run the following:
```
batch_niistats [option]
```
where [option] indicates which statistics to calculate for each .nii image, and must be one of: 
- `M`: calculate the mean of nonzero voxels
- `m`: calculate the mean of all voxels
- `S`: calculate the standard deviation of nonzero voxels
- `s`: calculate the standard deviation of all voxels

For example, to calculate the mean across only nonzero voxels for each image, type:
```
batch_niistats M
```

The program will start by opening a file selection dialogue box. Select the .csv file you created in step 1 and press ok. Wait for the program to finish.

When it is done you will have a .csv file in the same directory as the input .csv file. This output file has the same base name as the input file but with an added timestamp and a suffix that denotes the option specified as input. 

# Installation
There are a couple different ways to install `batch_niistats`. Regardless of the method you choose, it is recommended that you run the install inside a virtual environment per python best practices (see below). 

### 1. From PyPI
You can install a stable version of `batch_niistats` from PyPI using the command: 
```
pip install batch-niistats
```
> [!NOTE]
> Note that the pypi package uses a dash instead of an underscore

You can also update your current version of `batch_niistats` using the command: 
```
pip install --upgrade batch-niistats
```
### 2. From GitHub
For a version with the latest features and bug fixes, you can install `batch_niistats` from the source repository with the command `pip install git+https://github.com/mcclaskey/batch_niistats.git@main` or by cloning the repository and installing from the local directory (recommended). 

To install from a local directory, first cd to where you store all repos, create or activate your project environment (if using), and run the following:
```
git clone https://github.com/mcclaskey/batch_niistats.git
cd batch_niistats
pip install -e .
```
If you used a local install, you can easily update the code at a later date using the following lines:

```
git pull
pip install -e .
```

## A note on virtual environments if you are new to python's venv (disclaimer: personal opinions included)
If you don't already have a way to manage python environments and are looking to find one, I highly recommend Doug Hellmann's [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) tool. It's a clean, organized, and user-friendly wrapper for Ian Bicking's [virtualenv](https://pypi.org/project/virtualenv/) that stores all your environments in one place and makes them easy to work with. 

Conda/Anaconda also provide tools for environment management, although I generally find these more difficult to use unless you work with them every day (in which case you probably don't need advice on venv). 

Otherwise, you can quickly set up and activate a Python environment for this project using these steps:

#### 1. Create a virtual environment (do this only once, before running `pip install`)
Navigate to wherever you would like to store your virtual environment. If you have cloned a local copy of `batch_niistats`, you could create the venv inside the repo after navigating into the project directory with `cd batch_niistats`.

Use this command if on Windows:
```
py -m venv batch_niistats_venv
```

If on macOS/linux (Posix):
```
python3 -m venv batch_niistats_venv
```

This creates a virtual environment called `batch_niistats_venv`.

#### 2. Activate the environment each time you want to work on the project
Before working on the project, activate the environment using the appropriate command for your OS and shell (see the table on [this page](https://docs.python.org/3/library/venv.html#how-venvs-work) for exact syntax), together with your environment's full path.
