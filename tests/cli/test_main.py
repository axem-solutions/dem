"""Unit tests for running the dem in CLI mode without commands."""
# tests/cli/test_main_options.py

# Unit under test
import dem.cli.main as main

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import importlib.metadata, typer

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

def test_autocomplete_dev_env_name():
    # Test setup
    mock_platform = MagicMock()
    mock_dev_env = MagicMock()
    mock_dev_env.name = "TeSt"
    mock_platform.local_dev_envs = [
        mock_dev_env
    ]
    main.platform = mock_platform

    expected_completions = [mock_dev_env.name]

    # Run unit under test
    actual_completions = []
    for result in main.autocomplete_dev_env_name("TeS"):
        actual_completions.append(result)

    # Check expectations
    assert expected_completions == actual_completions

def test_autocomplete_cat_name():
    # Test setup
    mock_platform = MagicMock()
    fake_catalog_config = {
        "name": "test"
    }
    mock_platform.dev_env_catalogs.list_catalog_configs.return_value = [fake_catalog_config]
    main.platform = mock_platform

    expected_completions = [fake_catalog_config["name"]]

    # Run unit under test
    actual_completions = []
    for result in main.autocomplete_cat_name("tes"):
        actual_completions.append(result)

    # Check expectations
    assert expected_completions == actual_completions

def test_autocomplete_reg_name():
    # Test setup
    mock_platform = MagicMock()
    fake_registry_config = {
        "name": "test"
    }
    mock_platform.registries.list_registry_configs.return_value = [fake_registry_config]
    main.platform = mock_platform

    expected_completions = [fake_registry_config["name"]]

    # Run unit under test
    actual_completions = []
    for result in main.autocomplete_reg_name("tes"):
        actual_completions.append(result)

    # Check expectations
    assert expected_completions == actual_completions

@patch("dem.cli.main.__app_name__", "axem-dem")
@patch("dem.cli.main.stdout.print")
@patch("dem.cli.main.importlib.metadata.version")
def test_version_as_installed(mock_importlib_metadata_version, mock_stdout_print):
    # Test setup
    test_version = "0.1.2"
    mock_importlib_metadata_version.return_value = test_version

    # Run unit under test
    result = runner.invoke(main.typer_cli, ["--version"])

    # Check expectations
    assert result.exit_code == 0

    mock_stdout_print.assert_called_once_with("[cyan]" + main.__app_name__ + " v" + test_version + "[/]")

@patch("dem.cli.main.stdout.print")
@patch("dem.cli.main.importlib.metadata.version")
def test_version_as_module(mock_importlib_metadata_version, mock_stdout_print):
    # Test setup
    mock_importlib_metadata_version.side_effect = importlib.metadata.PackageNotFoundError()

    # Run unit under test
    result = runner.invoke(main.typer_cli, ["-v"])

    # Check expectations
    assert result.exit_code == 0

    mock_stdout_print.assert_called_once_with("[yellow]Install DEM to get the version number.[/]")

@patch("dem.cli.main.__app_name__", "axem-dem")
@patch("dem.cli.main.stdout.print", MagicMock())
@patch("dem.cli.main.importlib.metadata.version")
def test_version_exit_raised(mock_importlib_metadata_version):
    # Test setup
    test_version = "0.1.2"
    mock_importlib_metadata_version.return_value = test_version

    # Run unit under test
    with pytest.raises(typer.Exit):
        main._version_callback(True)

def test_platform_not_initialized():
    # Test setup
    test_dev_env_name = "test_dev_env_name"
    test_path = "test_path"
    test_name = "test_name"
    test_url = "test_url"
    mock_ctx = MagicMock()
    main.platform = None

    units_to_test = {
        main.list_: [],
        main.info: [test_dev_env_name],
        main.pull: [test_dev_env_name],
        main.cp: [test_dev_env_name, test_dev_env_name],
        main.create: [test_dev_env_name],
        main.export: [test_dev_env_name],
        main.load: [test_path],
        main.rename: [test_dev_env_name, test_dev_env_name],
        main.modify: [test_dev_env_name],
        main.delete: [test_dev_env_name],
        main.run: [test_dev_env_name, mock_ctx],
        main.add_reg: [test_name, test_url],
        main.list_reg: [],
        main.del_reg: [test_name],
        main.add_cat: [test_name, test_url],
        main.list_cat: [],
        main.del_cat: [test_name],
        main.add_host: [test_name, test_url]
    }

    for function, parameter in units_to_test.items():
        with pytest.raises(main.InternalError) as exported_exception_info:
            # Run unit under test
            function(*parameter)

            # Check expectations
            assert str(exported_exception_info) == "Error: The platform hasn't been initialized properly!"