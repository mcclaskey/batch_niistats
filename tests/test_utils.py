import os
import pytest
from batch_niistats.modules import utils
import pandas as pd
import numpy as np

def test_get_timestamp():
    """Test the timestamp generation"""
    timestamp = utils.get_timestamp()
    assert isinstance(timestamp, str)
    assert len(timestamp) > 0
    # Check that it follows the expected format "YYYY.MM.DD HH:MM:SS"
    assert len(timestamp.split(" ")) == 2
    date_part, time_part = timestamp.split(" ")
    assert len(date_part.split(".")) == 3
    assert len(time_part.split(":")) == 3

def test_parse_inputs():
    """Test the parsing of input options"""
    assert utils.parse_inputs('M') == {'omit_zeros': True, 'statistic': 'mean'}
    assert utils.parse_inputs('m') == {'omit_zeros': False, 'statistic': 'mean'}
    assert utils.parse_inputs('S') == {'omit_zeros': True, 'statistic': 'sd'}
    assert utils.parse_inputs('s') == {'omit_zeros': False, 'statistic': 'sd'}
    assert utils.parse_inputs('X') == {}

def test_askfordatalist(monkeypatch):
    """Test the askfordatalist function with a mock file dialog"""
    # Monkeypatch the filedialog.askopenfilename method to simulate file selection
    monkeypatch.setattr("tkinter.filedialog.askopenfilename", lambda: "tests/data/sample_datalist.csv")
    result = utils.askfordatalist()
    assert result == "tests/data/sample_datalist.csv"

def test_comma_split():
    result = utils.comma_split("path/to/file.nii,2")
    assert result == {'file': 'path/to/file.nii', 'volume_spm_0basedindex': 1}

def test_parse_spmsyntax_basic():
    # Sample datalist with 3 entries, one of which has SPM-style volume index
    data = {
        "input_file": [
            "subj1_func.nii,1",
            "subj2_func.nii,2",
            "subj3_func.nii"  # No comma
        ]
    }
    df = pd.DataFrame(data)
    
    result = utils.parse_spmsyntax(df)

    # Check that original columns are retained
    assert "input_file" in result.columns
    assert "file" in result.columns
    assert "volume_spm_0basedindex" in result.columns

    # Confirm split worked as expected
    assert result.iloc[0]['input_file'] == "subj1_func.nii,1"
    assert result.iloc[0]['file'] == "subj1_func.nii"
    assert result.iloc[0]['volume_spm_0basedindex'] == 0

    assert result.iloc[1]['input_file'] == "subj2_func.nii,2"
    assert result.iloc[1]['file'] == "subj2_func.nii"
    assert result.iloc[1]['volume_spm_0basedindex'] == 1

    # Handle row without a comma
    assert result.iloc[2]['input_file'] == "subj3_func.nii"
    assert result.iloc[2]['file'] == "subj3_func.nii"
    assert pd.isna(result.iloc[2]['volume_spm_0basedindex'])
    #assert result.iloc[2]['volume_spm_0basedindex'] == None  # dont yet code 1st vol (wait till later)

def test_parse_spmsyntax_missing_input_file_column():
    df = pd.DataFrame(columns=["other_column"])
    with pytest.raises(KeyError):
        utils.parse_spmsyntax(df)

def test_parse_spmsyntax_malformed_entries():
    # Handle unexpected input formats
    data = {
        "input_file": [
            "subj_func.nii,abc",  # non-integer index
            "subj_func.nii,2",
            "bad_format"          # no comma
        ]
    }
    df = pd.DataFrame(data)
    result = utils.parse_spmsyntax(df)

    assert result.iloc[0]['file'] == "subj_func.nii"
    assert pd.isna(result.iloc[0]['volume_spm_0basedindex'])
                   
    assert result.iloc[1]['file'] == "subj_func.nii"
    assert result.iloc[1]['volume_spm_0basedindex'] == 1

    assert result.iloc[2]['file'] == "bad_format"
    assert pd.isna(result.iloc[2]['volume_spm_0basedindex'])

def test_prioritize_volume_matching_volumes():
    df = pd.DataFrame({
        "input_file": ["dki_kfa.nii", "fmri_4d.nii.gz"],
        "volume_spm_0basedindex": [1, 2],
        "volume_0basedindex": [1, 2]
    })
    result = utils.prioritize_volume(df.copy())
    assert all(result["volume_0basedindex"] == [1, 2])

def test_prioritize_volume_user_preferred_when_conflict():
    df = pd.DataFrame({
        "input_file": ["dki_kfa.nii", "fmri_4d.nii.gz"],
        "volume_spm_0basedindex": [1, 2],
        "volume_0basedindex": [3, 4]
    })
    result = utils.prioritize_volume(df.copy())
    assert all(result["volume_0basedindex"] == [3, 4])

def test_prioritize_volume_use_spm_when_user_missing():
    df = pd.DataFrame({
        "input_file": ["dki_kfa.nii", "fmri_4d.nii.gz"],
        "volume_spm_0basedindex": [5, 6],
        "volume_0basedindex": [np.nan, np.nan]
    })
    result = utils.prioritize_volume(df.copy())
    assert all(result["volume_0basedindex"] == [5, 6])

def test_prioritize_volume_default_to_zero_when_both_missing():
    df = pd.DataFrame({
        "input_file": ["dki_kfa.nii", "fmri_4d.nii.gz"],
        "volume_spm_0basedindex": [np.nan, np.nan],
        "volume_0basedindex": [np.nan, np.nan]
    })
    result = utils.prioritize_volume(df.copy())
    assert all(result["volume_0basedindex"] == [0, 0])

def test_prioritize_volume_mixed_cases():
    df = pd.DataFrame({
        "input_file": ["dki_kfa.nii", "fmri_4d.nii.gz","dki_kfa.nii", "fmri_4d.nii.gz"],
        "volume_spm_0basedindex": [1, 5, np.nan, np.nan],
        "volume_0basedindex": [1, 4, np.nan, 9]
    })
    # Expect:
    # - file1: match → use 1
    # - file2: conflict → use user 4
    # - file3: spm only → use 0 (default)
    # - file4: user only → use 9
    result = utils.prioritize_volume(df.copy())
    assert result["volume_0basedindex"].tolist() == [1, 4, 0, 9]

def test_load_datalist_singlecolumnsinglecolumn():
    """Test loading and parsing the .csv datalist"""
    # Prepare a mock CSV file
    #datalist_filepath = "tests/data/sample_datalist_3D.csv"
    datalist_filepath = os.path.join(os.path.dirname(__file__), "data", "sample_datalist.csv")
    datalist = utils.load_datalist(datalist_filepath)
    
    assert isinstance(datalist, pd.DataFrame)
    assert 'input_file' in datalist.columns
    assert 'file' in datalist.columns
    assert 'volume_0basedindex' in datalist.columns