import numpy as np
import pytest
from batch_niistats.modules import nii

list_of_inputs_to_decorate = [
    ({"statistic": "mean", "omit_zeros": True},
     "mean of nonzero voxels", 0.279955),
    ({"statistic": "mean", "omit_zeros": False},
     "mean of all voxels", 0.069626),
    ({"statistic": "sd", "omit_zeros": True},
     "sd of nonzero voxels", 0.174159),
    ({"statistic": "sd", "omit_zeros": False},
     "sd of all voxels", 0.148956)
]


def test_load_3d_nii():
    """Test loading a 3D .nii file"""
    nii_file = 'tests/data/dki_kfa.nii'
    gz_file = 'tests/data/dki_kfa.nii.gz'
    volume = 0  # Specify volume index for testing
    data = nii.load_nii(nii_file, volume)
    zipdata = nii.load_nii(gz_file, volume)

    assert isinstance(data, np.ndarray)
    assert isinstance(zipdata, np.ndarray)
    assert data.ndim == 3
    assert zipdata.ndim == 3


def test_load_4d_nii():
    """Test loading a 4D .nii file"""
    nii_file = 'tests/data/fmri_4d.nii.gz'
    data_vol0 = nii.load_nii(nii_file, 0)  # first volume
    data_vol1 = nii.load_nii(nii_file, 1)  # second volume

    assert isinstance(data_vol0, np.ndarray)
    assert isinstance(data_vol1, np.ndarray)
    assert data_vol0.ndim == 3
    assert data_vol1.ndim == 3
    assert np.any(np.not_equal(data_vol1, data_vol0))
    np.testing.assert_raises(AssertionError,
                             np.testing.assert_array_equal,
                             data_vol1,
                             data_vol0)


def test_mean_nii():
    """Test mean calculation on a .nii file"""
    nii_file = 'tests/data/dki_kfa.nii'
    data = nii.load_nii(nii_file, 0)

    # Calculate mean including and excluding zeros
    mean_all = nii.mean_nii(data, omit_zeros=False)
    mean_nonzero = nii.mean_nii(data, omit_zeros=True)

    assert isinstance(mean_all, float)
    assert isinstance(mean_nonzero, float)
    assert np.isclose(mean_all, .069626, atol=0.01)
    assert np.isclose(mean_nonzero, .279955, atol=0.01)


def test_sd_nii():
    """Test standard deviation calculation on a .nii file"""
    nii_file = 'tests/data/dki_kfa.nii'
    data = nii.load_nii(nii_file, 0)

    # Calculate standard deviation including and excluding zeros
    sd_all = nii.sd_nii(data, omit_zeros=False)
    sd_nonzero = nii.sd_nii(data, omit_zeros=True)

    assert isinstance(sd_all, float)
    assert isinstance(sd_nonzero, float)
    assert np.isclose(sd_all, 0.148956, atol=0.01)
    assert np.isclose(sd_nonzero, .174159, atol=0.01)


@pytest.mark.parametrize("inputs, expected_statistic, answer",
                         list_of_inputs_to_decorate)
def test_single_nii_calc(inputs, expected_statistic, answer):
    """Calculate statistics for a single file that exists"""
    # Assuming that 'valid_files' contains files in the correct directory
    nii_rawinput = 'tests/data/dki_kfa.nii, 1'
    nii_file = 'tests/data/dki_kfa.nii'
    result = nii.single_nii_calc(nii_rawinput,
                                 nii_file,
                                 0,
                                 inputs,
                                 {nii_file})
    assert isinstance(result, dict)
    assert result["input_file"] == nii_rawinput
    assert result["filename"] == nii_file
    assert result['volume_0basedindex'] == 0
    assert expected_statistic in result
    assert np.isclose(result[expected_statistic], answer, atol=0.01)
    assert result['note'] == 'file exists'


@pytest.mark.parametrize("inputs, expected_statistic, answer",
                         list_of_inputs_to_decorate)
def test_single_nii_calc_nonexistentfile(inputs, expected_statistic, answer):
    """Calculate statistics for a single file that doesn't exist"""
    # Assuming that 'valid_files' contains files in the correct directory
    nii_rawinput = 'tests/data/dki_kfa_missing.nii, 1'
    nii_file = 'tests/data/dki_kfa_missing.nii'
    valid_files = {'tests/data/dki_kfa.nii'}
    result = nii.single_nii_calc(nii_rawinput,
                                 nii_file,
                                 0,
                                 inputs,
                                 valid_files)
    assert isinstance(result, dict)
    assert result["input_file"] == nii_rawinput
    assert result["filename"] == nii_file
    assert result['volume_0basedindex'] == 0
    assert expected_statistic in result
    assert result[expected_statistic] is None
    assert result['note'] == 'file not found'


@pytest.mark.parametrize("inputs, expected_statistic, answer",
                         list_of_inputs_to_decorate)
def test_try_single_nii_calc(inputs, expected_statistic, answer):
    """Calculate statistics for a single file that exists"""
    # Assuming that 'valid_files' contains files in the correct directory
    nii_rawinput = 'tests/data/dki_kfa.nii, 1'
    nii_file = 'tests/data/dki_kfa.nii'
    result = nii.try_single_nii_calc(
        nii_rawinput,
        nii_file,
        0,
        inputs,
        {nii_file})
    assert isinstance(result, dict)
    assert result["input_file"] == nii_rawinput
    assert result["filename"] == nii_file
    assert result['volume_0basedindex'] == 0
    assert expected_statistic in result
    assert np.isclose(result[expected_statistic], answer, atol=0.01)
    assert result['note'] == 'file exists'


@pytest.mark.parametrize("inputs, expected_statistic, answer",
                         list_of_inputs_to_decorate)
def test_try_single_nii_calc_nonexistentfile(inputs,
                                             expected_statistic,
                                             answer):
    """Calculate statistics for a single file that doesn't exist"""
    # Assuming that 'valid_files' contains files in the correct directory
    nii_rawinput = 'tests/data/dki_kfa_missing.nii, 1'
    nii_file = 'tests/data/dki_kfa_missing.nii'
    valid_files = {'tests/data/dki_kfa.nii'}
    result = nii.try_single_nii_calc(
        nii_rawinput,
        nii_file,
        0,
        inputs,
        valid_files)
    assert isinstance(result, dict)
    assert result["input_file"] == nii_rawinput
    assert result["filename"] == nii_file
    assert result['volume_0basedindex'] == 0
    assert expected_statistic in result
    assert result[expected_statistic] is None
    assert result['note'] == 'file not found'


@pytest.mark.parametrize("inputs, expected_statistic, answer",
                         list_of_inputs_to_decorate)
def test_try_single_nii_calc_error(mocker, inputs, expected_statistic, answer):
    """Calculate statistics for a single file but run error"""

    nii_rawinput = 'tests/data/dki_kfa.nii, 1'
    nii_file = 'tests/data/dki_kfa.nii'
    valid_files = {'tests/data/dki_kfa.nii'}

    # create mock exception and capture error
    mock_single_nii_calc = mocker.patch(
        'batch_niistats.cli.nii.single_nii_calc',
        side_effect=Exception("Test error")
        )
    mock_print = mocker.patch("builtins.print")

    result = nii.try_single_nii_calc(
        nii_rawinput,
        nii_file,
        0,
        inputs,
        valid_files)

    # checks
    mock_single_nii_calc.assert_called_once_with(nii_rawinput,
                                                 nii_file,
                                                 0,
                                                 inputs,
                                                 valid_files)
    mock_print.assert_called_once_with(
        f"Error processing {nii_file}: Test error"
        )
    assert result is None
