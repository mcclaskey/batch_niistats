# batch_niistats
Small set of functions that take a list of 2D nifti files and return a .csv file that contains the mean value of each image. Pure python code that works very quickly on all operating systems.

The mean value of each .nii file can be calculated for all voxels in the .nii, or for all nonzero voxels. This is the equivalent of fslstats with the -M option or -m option, respectively.

# Requirements
* python3.11+

# Instructions

## 1. Create a list of .nii files
Put together a list of your .nii files and save this list as a single-column .csv file where the first row says "input_file" and each subsequent row contains the full file path to a .nii file. Each .nii file will have its average value calculated.

> [!IMPORTANT]
> The first row of the .csv must say "input_file"

## 2. Run scripts 

Open a terminal and activate your project environment and cd to the project directory, then run the following line:
```
python3 batch_niistats.py [option]
```
where [option] indicates which statistics to output for each .nii image, and must be one of: 
- `-M`: calculate the mean of all nonzero voxels
- `-m`: calculate the mean value of all voxels
- `-S`: calculate the standard deviation of all nonzero voxels
- `-s`: calculate the standard deviation of all voxels

For example, to calculate mean across all nonzero voxels, type:

```
python3 batch_niistats.py -M
```

The program will start by opening a file selection dialogue box. Select the .csv file you created in step 1 and press ok. Wait while the program runs.

When it is done you will have a .csv file in the same directory as the input .csv file. The output file's name will be be the same as the input file's name but will have a timestamp and the suffix that indicates the option specified as input. 

# Setup 
1. create/activate a project environment
2. cd to where you store repos and clone this repo using `git clone https://github.com/mcclaskey/batch_niistats.git`
3. cd to repo directory
4. run `pip3 install -r requirements.txt` to install required packages into your environment
