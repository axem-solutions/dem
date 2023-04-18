"""Tests for the rename CLI command."""
# tests/cli/test_rename_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.rename_cmd as rename_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from rich.console import Console
import io

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
def test_check_dev_env_name_exist():
    # Test setup
    test_name = "dev_env_name"
    fake_dev_env = MagicMock()
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env

    # Run unit under test
    actual_dev_env = rename_cmd.check_dev_env_name_exist(dev_env_local_setup, test_name)

    # Check expectations
    assert actual_dev_env is None

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_name)

@patch("dem.cli.command.rename_cmd.stderr.print")
def test_check_dev_env_name_not_exist(mock_stderr_print):
    # Test setup
    fake_name = "fake_env_name"
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = None

    # Run unit under test
    actual_dev_env = rename_cmd.check_dev_env_name_exist(dev_env_local_setup, fake_name)

    # Check expectations
    assert -1 == actual_dev_env 

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(fake_name)
    mock_stderr_print.assert_called_once_with("[red]Error: The input Development Environment does not exist.[/]")

@patch("dem.cli.command.rename_cmd.stderr.print")
def test_rename_given_dev_env_error(mock_stderr_print):
    # Test setup
    test_name = "dev_env_name"    
    test_new_name = "test_new_name"
    fake_deserialized_dev_env_org_json = MagicMock()

    # Run unit under test
    result = rename_cmd.rename_given_dev_env(fake_deserialized_dev_env_org_json,
                                             test_new_name,
                                             test_name)

    # Check expectations
    assert -1 == result 

    mock_stderr_print.assert_called_once_with("[red]Error: Unable to rename the Development Environment.[/]")

def test_rename_given_dev_env():
    # Test setup
    test_name = "dev_env_to_rename"    
    test_new_name = "test_new_name"
    fake_deserialized_dev_env_org_json = {
        "development_environments": [
            {
                "name": "dev_env_name"
            },
            {
                "name": "dev_env_to_rename"
            }
        ]
    }

    # Run unit under test
    result = rename_cmd.rename_given_dev_env(fake_deserialized_dev_env_org_json, test_name,
                                             test_new_name)

    # Check expectations
    assert None == result 
    expected_deserialized_dev_env_org_json = {
        "development_environments": [
            {
                "name": "dev_env_name"
            },
            {
                "name": "test_new_name"
            }
        ]
    }
    assert expected_deserialized_dev_env_org_json == fake_deserialized_dev_env_org_json

@patch("dem.cli.command.rename_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.rename_cmd.rename_given_dev_env")
@patch("dem.cli.command.rename_cmd.check_dev_env_name_exist")
@patch("dem.cli.command.rename_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.rename_cmd.DevEnvLocalSetup")
def test_rename_success(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_json, 
                        mock_check_dev_env_name_exist, mock_rename_given_dev_env,
                        mock_write_deserialized_dev_env_json):
    # Test setup
    original_dev_env_name = "original_dev_env_name"
    new_dev_env_name = "new_dev_env_name"
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    mock_check_dev_env_name_exist.return_value = None

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, 
                                  ["rename", original_dev_env_name, new_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_local_dev_env)
    mock_check_dev_env_name_exist.assert_called_once_with(fake_dev_env_local_setup, 
                                                          original_dev_env_name)
    mock_rename_given_dev_env.assert_called_once_with(fake_deserialized_local_dev_env, 
                                                      original_dev_env_name, 
                                                      new_dev_env_name)
    mock_write_deserialized_dev_env_json.assert_called_once_with(fake_deserialized_local_dev_env)

@patch("dem.cli.command.rename_cmd.check_dev_env_name_exist")
@patch("dem.cli.command.rename_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.rename_cmd.DevEnvLocalSetup")
def test_rename_non_existing(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_json, 
                             mock_check_dev_env_name_exist):
    # Test setup
    original_dev_env_name = "original_dev_env_name"
    new_dev_env_name = "new_dev_env_name"
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    mock_check_dev_env_name_exist.return_value = -1

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, 
                                  ["rename", original_dev_env_name, new_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_local_dev_env)
    mock_check_dev_env_name_exist.assert_called_once_with(fake_dev_env_local_setup, 
                                                          original_dev_env_name)