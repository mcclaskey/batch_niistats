import pytest
import sys
from batch_niistats import cli
import pandas as pd
import numpy as np
import subprocess
import os


@pytest.mark.parametrize("args, expected_statistic, answer", [
    (["M"], "mean of nonzero voxels",
     pd.Series([1039.369187, 1039.347735, 1039.369187,
                0.279955, 0.279955, np.nan])),
    (["m"], "mean of all voxels",
     pd.Series([880.965488, 880.965823, 880.965488,
                0.069626, 0.069626, np.nan])),
    (["S"], "sd of nonzero voxels",
     pd.Series([1738.948744, 1736.483171, 1738.948744,
                0.174158, 0.174159, np.nan])),
    (["s"], "sd of all voxels",
     pd.Series([1643.971591, 1641.771553, 1643.971591,
                0.148956, 0.148956, np.nan]))
])
def test_cli_main_with_datalist1(mocker, args, expected_statistic, answer):
    "Tests entire script with first sample datalist"
    sample_datalist_path = "tests/data/sample_datalist.csv"
    mocker.patch("batch_niistats.cli.utils.askfordatalist",
                 return_value=sample_datalist_path)
    mock_save = mocker.patch("batch_niistats.cli.utils.save_output_csv",
                             return_value=None)

    # Run the main function with the given arguments
    sys.argv = ["batch_niistats.py"] + args
    test_result = cli.main()

    # check the output
    mock_save.assert_called_once()
    assert not test_result.empty
    assert isinstance(test_result, pd.DataFrame)
    assert test_result.ndim == 2
    assert test_result.shape == (6, 5)
    assert expected_statistic in test_result.columns
    assert np.allclose(test_result[expected_statistic],
                       answer, atol=0.01,
                       equal_nan=True)
    assert test_result.loc[5, "note"] == "file not found"


@pytest.mark.parametrize("args, expected_statistic, answer", [
    (["M"], "mean of nonzero voxels",
     pd.Series([np.nan, 1039.369187, 1039.347735, 1039.347735, 1039.369187,
                1039.347735, 1039.369187, 1039.347735, 1039.369187,
                0.279955, 0.279955, 0.279955, 0.279955, np.nan])),
    (["m"], "mean of all voxels",
     pd.Series([np.nan, 880.965488, 880.965823, 880.965823, 880.965488,
                880.965823, 880.9654887, 880.965823, 880.965488,
                0.069626, 0.069626, 0.069626, 0.069626, np.nan])),
    (["S"], "sd of nonzero voxels",
     pd.Series([np.nan, 1738.948744, 1736.483171, 1736.483171, 1738.948744,
                1736.483171, 1738.9487447, 1736.483171, 1738.948744,
                0.174158, 0.174158, 0.174158, 0.174158, np.nan])),
    (["s"], "sd of all voxels",
     pd.Series([np.nan, 1643.971591, 1641.771553, 1641.771553, 1643.971591,
                1641.771553, 1643.971591, 1641.771553, 1643.971591,
                0.148956, 0.148956, 0.148956, 0.148956, np.nan])),
])
def test_cli_main_with_datalist2(mocker, args, expected_statistic, answer):
    "Tests entire script with second sample datalist"
    sample_datalist_path = "tests/data/sample_datalist_volumecol.csv"
    mocker.patch("batch_niistats.cli.utils.askfordatalist",
                 return_value=sample_datalist_path)
    mock_save = mocker.patch("batch_niistats.cli.utils.save_output_csv",
                             return_value=None)

    # Run the main function with the given arguments
    sys.argv = ["batch_niistats.py"] + args
    test_result = cli.main()

    # check the output
    mock_save.assert_called_once()
    assert not test_result.empty
    assert isinstance(test_result, pd.DataFrame)
    assert test_result.ndim == 2
    assert test_result.shape == (14, 5)
    assert expected_statistic in test_result.columns
    assert np.allclose(test_result[expected_statistic],
                       answer,
                       atol=0.01,
                       equal_nan=True)
    assert test_result.loc[0, "note"] == "file not found"
    assert test_result.loc[13, "note"] == "file not found"


@pytest.mark.parametrize("args, expected_statistic, answer", [
    (["M"], "mean of nonzero voxels", 1039.369187),
    (["m"], "mean of all voxels", 880.965488),
    (["S"], "sd of nonzero voxels", 1738.948744),
    (["s"], "sd of all voxels", 1643.971591),
])
def test_cli_main_with_datalist3(mocker, args, expected_statistic, answer):
    "Tests entire script with third sample datalist"
    # Mock user prompts and file saves
    sample_datalist_path = "tests/data/sample_datalist_nospmsyntax.csv"
    mocker.patch("batch_niistats.cli.utils.askfordatalist",
                 return_value=sample_datalist_path)
    mock_save = mocker.patch("batch_niistats.cli.utils.save_output_csv",
                             return_value=None)

    # Run the main function with the given arguments
    sys.argv = ["batch_niistats.py"] + args
    test_result = cli.main()

    # check the output
    mock_save.assert_called_once()
    assert not test_result.empty
    assert isinstance(test_result, pd.DataFrame)
    assert test_result.ndim == 2
    assert test_result.shape == (1, 5)
    assert expected_statistic in test_result.columns
    assert np.allclose(test_result[expected_statistic],
                       answer,
                       atol=0.01,
                       equal_nan=True)


def test_cli_invalid_option(mocker):
    """Checks that an invalid option triggers the proper error handling"""
    sys.argv = ["batch_niistats.py", "-invalid_option"]

    # Mock the `askfordatalist` to simulate the process
    mocker.patch("batch_niistats.cli.utils.askfordatalist",
                 return_value="./data/sample_datalist_3D.csv")

    # Mock the function that prints to the console
    mocker.patch("builtins.print")

    # Run the main function and expect it to print usage info
    with pytest.raises(SystemExit):  # invalid argument
        cli.main()


def test_cli_entrypoint_runs():
    """checks that main is called"""
    script_path = os.path.join(os.path.dirname(__file__),
                               "..",
                               "src",
                               "batch_niistats",
                               "cli.py")
    script_path = os.path.abspath(script_path)

    # Run it with a help argument to avoid running the whole thing
    result = subprocess.run([sys.executable,
                             script_path, "--help"],
                            capture_output=True,
                            text=True,
                            input="\n",
                            timeout=10)
    assert result.returncode == 0
    assert "usage:" in result.stdout
