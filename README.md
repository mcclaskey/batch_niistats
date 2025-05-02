# batch_niistats: calculate statistics on a batch of 3D NIfTI files
[![Python Versions](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-blue)](https://pypi.org/project/batch-niistats/) [![PyPI version](https://img.shields.io/pypi/v/batch-niistats.svg?color=orange)](https://pypi.org/project/batch-niistats/)
 [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/mcclaskey/batch_niistats/blob/main/LICENSE) [![batch_niistats-tests](https://img.shields.io/github/actions/workflow/status/mcclaskey/batch_niistats/python-package.yml?label=batch_niistats-tests&logo=github)](https://pypi.org/project/batch-niistats/) [![codecov](https://codecov.io/gh/mcclaskey/batch_niistats/branch/main/graph/badge.svg)](https://pypi.org/project/batch-niistats/) 


Calculate statistics on a batch of 3D NIfTI files and return the output as a `.csv` file. Statistics (mean/standard deviation) can be calculated for all voxels in the 3D nifti, or for only nonzero voxels. 

`batch_niistats` can read both zipped (`.nii.gz`) and unzipped (`.nii`) NIfTI files.

## Requirements
* python3.11+

# Instructions

### 1. Create a list of NIfTI files
Create a `.csv` file that lists the 3D NIfTI files to process, with the following structure:
- the first column contains the full paths to your 3D NIfTI files, including the extension (`.nii` or `nii.gz`)
- the first column's header is `input_file` 

Statistics are calculated only for 3D volumes, and each input row must point to a single volume of a file (or a single 3D NIfTI file). 

#### If you have 4D files:
To calculate statistics on a volume other than the first, add a second column called `volume_0basedindex` that specifies which volume to read using **0-based indexing** (_e.g._ `0` for the first volume, `1` for the second, etc). 0-based indexing matches the conventions of python, NiBabel, FSL, etc. To read multiple volumes of the same 4D nifti file, list each volume as a separate row in the input `.csv` file.

Alternatively, you can specify the volume using SPM-style syntax in the `input_file` column, as follows: 
```
full\path\to\your.nii,V
```
where V is an integer that indicates the volume number using **1-based indexing**, _e.g._ `path\to\my.nii,1` for the first volume of `my.nii`. 

Support for SPM syntax is intended to facilitate copying to and from SPM but is otherwise not recommended. If you define filenames in this way, omit single quotations at the start and end of each string that are sometimes retained during SPM copy/paste. `batch_niistats` does not strip single quotations from file paths because they could be valid characters in some filenames.

If volumes are specified using both SPM syntax and using a `volume_0basedindex` column, the information in the `volume_0basedindex` column will be preferentially used. If no information is provided, `batch_niistats` will read the first volume of each image by default.

### 2. Call `batch_niistats` 

Open a terminal (in Unix/Linux/WSL) or command prompt (in Windows), activate your virtual environment (if necessary), then run the following:
```
batch_niistats OPTION
```
where `OPTION` indicates which statistics to calculate for each .nii image, and is one of: 
- `M`: calculate the mean of nonzero voxels
- `m`: calculate the mean of all voxels
- `S`: calculate the standard deviation of nonzero voxels
- `s`: calculate the standard deviation of all voxels

For example, to calculate the mean across only nonzero voxels for each image, type:
```
batch_niistats M
```

When prompted with a file selection dialogue, select the `.csv` file you created in step 1 and press ok. Wait for the program to finish.

Once complete, the program will generate an output `.csv` with the calculated statistics and notes on each file. This output `.csv` is saved to the same directory as the input `.csv` file and its filename will include the timestamp and a suffix denoting the option specified as input. 

# Installation
You can install `batch_niistats` either from PyPI or GitHub. Using a virtual environment is strongly recommended (see below).

### 1. Install from PyPI
Install a stable version of `batch_niistats` from PyPI using the command: 
```
pip install batch-niistats
```

> **⚠️ IMPORTANT**  
> When installing from pypi, use a dash instead of an underscore in the package name


To upgrade an existing install, use: 
```
pip install --upgrade batch-niistats
```
### 2. Install from GitHub (for latest features and bug fixes)
You can install `batch_niistats` from the source repository with the command `pip install git+https://github.com/mcclaskey/batch_niistats.git@main`, or by cloning the repository and installing from the local directory (recommended). 

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
If you need a way to manage python environments, I highly recommend Doug Hellmann's [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/). It's a clean, organized, and user-friendly wrapper for Ian Bicking's [virtualenv](https://pypi.org/project/virtualenv/) that stores all your environments in one place with minimal fuss. It's built for POSIX but there is a Windows version [here](https://pypi.org/project/virtualenvwrapper-win/). 

Conda/Anaconda also provides tools for environment management, although I generally find these more difficult to use unless you work with them every day (in which case you probably don't need advice on venv). 

Otherwise, you can quickly set up and activate a Python environment for this project using these steps:

#### 1. Create a virtual environment (do this only once, before running `pip install`)
Navigate to wherever you would like to store your virtual environment. Create the environment using the following:

If on Windows:
```
py -m venv batch_niistats_venv
```

If on macOS/linux (Posix):
```
python3 -m venv batch_niistats_venv
```

This creates a virtual environment called `batch_niistats_venv`.

> **💡 TIP**  
> If you have cloned a local copy of `batch_niistats`, you can create the virtual environment inside the repo by running the above command after navigating into the project directory with `cd batch_niistats` and before running `pip install`

#### 2. Activate the environment each time you want to work on the project
Before working on the project, activate the environment using the appropriate command for your OS and shell (see the table on [this page](https://docs.python.org/3/library/venv.html#how-venvs-work) for exact syntax), together with your environment's path.
