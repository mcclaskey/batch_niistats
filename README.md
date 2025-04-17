# batch_niistats
Small set of functions that use nibabel to calculate mean value of a set of .nii files.

# Requirements
* python3.11+

# Instructions

## 1. Create a list of .nii files
Put together a list of your .nii files and save this list as a single-column .csv file where the first row says "input_file" and each subsequent row contains the full file path to a .nii file. Each .nii file will have its average value calculated.

> [!IMPORTANT]
> The first row of the .csv must say "input_file"

## 2. Run scripts 

Open a terminal and run the following 2 lines:
```
workon batch_fslstats_env
python3 batch_niistats.py
```
A file selection dialogue box will now open. Select the .csv file you created in step 1 and press ok. Wait while the program runs.

When it is done you will have a .csv file in the same directory as the input .csv file. The output file's name will be be the same as the input filename but will have a timestamp and the suffix '*_compiled'.

# Setup (Advanced Users)
If you have and an established system for managing environments (such as conda or virtualenvwrapper), no special setup is needed: 
1. create/activate a project environment
2. cd to where you store repos and clone this repo, e.g. `git clone https://github.com/mcclaskey/batch_niistats.git`
3. cd to repo directory
4. run `pip install -r requirements.txt` to install required packages
