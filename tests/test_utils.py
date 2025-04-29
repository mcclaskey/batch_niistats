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
    assert utils.parse_inputs('M') == {'omit_zeros': True,
                                       'statistic': 'mean'}
    assert utils.parse_inputs('m') == {'omit_zeros': False,
                                       'statistic': 'mean'}
    assert utils.parse_inputs('S') == {'omit_zeros': True,
                                       'statistic': 'sd'}
    assert utils.parse_inputs('s') == {'omit_zeros': False,
                                       'statistic': 'sd'}
    assert utils.parse_inputs('X') == {}


def test_askfordatalist(mocker):
    """Test the askfordatalist function with a mock file dialog"""

    mock_tk_instance = mocker.Mock()
    mocker.patch("batch_niistats.modules.utils.tk.Tk",
                 return_value=mock_tk_instance)

    mock_askopenfilename = mocker.patch(
        "tkinter.filedialog.askopenfilename",
        return_value="tests/data/sample_datalist.csv"
        )
    result = utils.askfordatalist()

    assert result == "tests/data/sample_datalist.csv"
    assert mock_tk_instance.withdraw.call_count == 1
    assert mock_tk_instance.destroy.call_count == 1
    mock_askopenfilename.assert_called_once()


def test_comma_split():
    result = utils.comma_split("path/to/file.nii, 2")
    assert result == {'file': 'path/to/file.nii', 'volume_spm_0basedindex': 1}


def test_parse_spmsyntax_basic():
    # Sample datalist with 3 entries, one of which has SPM-style volume index
    data = {
        "input_file": [
            "subj1_func.nii, 1",  # space
            "subj2_func.nii,2",  # no space
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
    assert result.iloc[0]['input_file'] == "subj1_func.nii, 1"
    assert result.iloc[0]['file'] == "subj1_func.nii"
    assert result.iloc[0]['volume_spm_0basedindex'] == 0

    assert result.iloc[1]['input_file'] == "subj2_func.nii,2"
    assert result.iloc[1]['file'] == "subj2_func.nii"
    assert result.iloc[1]['volume_spm_0basedindex'] == 1

    # Handle row without a comma
    assert result.iloc[2]['input_file'] == "subj3_func.nii"
    assert result.iloc[2]['file'] == "subj3_func.nii"
    assert pd.isna(result.iloc[2]['volume_spm_0basedindex'])


def test_parse_spmsyntax_missing_input_file_column():
    df = pd.DataFrame(columns=["other_column"])
    with pytest.raises(KeyError):
        utils.parse_spmsyntax(df)


def test_parse_spmsyntax_malformed_entries():
    # Handle unexpected input formats
    data = {
        "input_file": [
            "subj_func.nii, abc",  # non-integer index
            "subj_func.nii, 2",
            "bad_format"  # no comma
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
        "input_file": ["dki_kfa.nii",
                       "fmri_4d.nii.gz",
                       "dki_kfa.nii",
                       "fmri_4d.nii.gz"],
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
    datalist_filepath = os.path.join(os.path.dirname(__file__),
                                     "data",
                                     "sample_datalist.csv")
    datalist = utils.load_datalist(datalist_filepath)

    assert isinstance(datalist, pd.DataFrame)
    assert 'input_file' in datalist.columns
    assert 'file' in datalist.columns
    assert 'volume_0basedindex' in datalist.columns


@pytest.mark.parametrize("statistic, datalist_filepath", [
    (["M"], "/path/to/datalist.csv"),
    (["m"], "/path/to/datalist.csv"),
    (["S"], "/path/to/another_datalist.csv"),
    (["s"], "/path/to/another_datalist.csv")
])
def test_generate_output_path(statistic, datalist_filepath):
    """Test writing output .csv full path with different inputs"""
    timestamp = "2025.04.28 12:34:56"
    statistic = "M"
    datalist_filepath = "/path/to/datalist.csv"

    # Expected output path
    expected_timestamp_file = "20250428_123456"
    expected_output_dir = os.path.dirname(datalist_filepath)
    expected_base_name = "datalist_calc_M.csv"
    expected_output_path = os.path.join(
        expected_output_dir,
        f"{expected_timestamp_file}_{expected_base_name}"
        )

    output_path = utils.write_output_df_path(datalist_filepath,
                                             statistic,
                                             timestamp)
    assert output_path == expected_output_path


def test_save_output_csv(mocker):
    # Create a sample DataFrame to use in the test
    output_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

    # Define the expected output path
    output_path = "/path/to/output_file.csv"

    # Mocking pandas DataFrame to_csv method to avoid file writing
    mock_to_csv = mocker.patch.object(pd.DataFrame, 'to_csv')
    mock_to_csv.return_value = None

    # Mocking the print function to capture printed messages
    mock_print = mocker.patch("builtins.print")

    # Call the function
    utils.save_output_csv(output_df, output_path)

    # Assert that the to_csv method was called w the expected arguments
    mock_to_csv.assert_called_once_with(output_path, index=False)

    # Assert that the print statement w the expected output message
    expected_print_message = f"\nOutput saved to file:\n{output_path}\n"
    mock_print.assert_called_once_with(expected_print_message)
