"""Tests for the create CLI command."""
# tests/cli/test_create_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from dem.core.dev_env_setup import DevEnv

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test helpers
## Test cases

@patch("dem.cli.command.create_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.create_cmd.DevEnvLocal")
@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.dev_env_name_check")
@patch("dem.cli.command.create_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.create_cmd.data_management.read_deserialized_dev_env_json")
def test_execute_dev_env_creation(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup,
                                  mock_dev_env_name_check, mock_get_dev_env_descriptor_from_user,
                                  mock_DevEnvLocal, mock_write_deserialized_dev_env_json):
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    mock_dev_env_name_check.return_value = None
    fake_dev_env_descriptor = MagicMock()
    mock_get_dev_env_descriptor_from_user.return_value = fake_dev_env_descriptor
    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_local_dev_env
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_local_dev_env)
    mock_dev_env_name_check.assert_called_once_with(fake_dev_env_local_setup, expected_dev_env_name)
    mock_get_dev_env_descriptor_from_user.assert_called_once_with(expected_dev_env_name)
    mock_DevEnvLocal.assert_called_once_with(fake_dev_env_descriptor)
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_json.assert_called_once_with(fake_deserialized_local_dev_env)

@patch("dem.cli.command.create_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.typer.confirm")
@patch("dem.cli.command.create_cmd.dev_env_name_check")
@patch("dem.cli.command.create_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.create_cmd.data_management.read_deserialized_dev_env_json")
def test_execute_dev_env_overwrite(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup,
                                   mock_dev_env_name_check, mock_confirm,
                                   mock_get_dev_env_descriptor_from_user,
                                   mock_write_deserialized_dev_env_json):
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_original = MagicMock()
    mock_dev_env_name_check.return_value = fake_dev_env_original
    fake_tools = MagicMock()
    fake_dev_env_descriptor = {
        "tools": fake_tools
    }
    mock_get_dev_env_descriptor_from_user.return_value = fake_dev_env_descriptor
    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_local_dev_env
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_local_dev_env)
    mock_dev_env_name_check.assert_called_once_with(fake_dev_env_local_setup, expected_dev_env_name)
    mock_confirm.assert_called_once_with("The input name is already used by a Development Environment. Overwrite it?",
                                         abort=True)
    mock_get_dev_env_descriptor_from_user.assert_called_once_with(expected_dev_env_name)
    assert fake_dev_env_original.tools == fake_tools
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_json.assert_called_once_with(fake_deserialized_local_dev_env)

@patch("dem.cli.command.create_cmd.get_dev_env_descriptor_from_user")
@patch("dem.cli.command.create_cmd.typer.confirm")
@patch("dem.cli.command.create_cmd.dev_env_name_check")
@patch("dem.cli.command.create_cmd.DevEnvLocalSetup")
@patch("dem.cli.command.create_cmd.data_management.read_deserialized_dev_env_json")
def test_execute_abort(mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup, 
                       mock_dev_env_name_check, mock_confirm, 
                       mock_get_dev_env_descriptor_from_user):
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_original = MagicMock()
    mock_dev_env_name_check.return_value = fake_dev_env_original
    mock_confirm.side_effect = Exception()
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_deserialized_local_dev_env)
    mock_dev_env_name_check.assert_called_once_with(fake_dev_env_local_setup, expected_dev_env_name)
    mock_confirm.assert_called_once_with("The input name is already used by a Development Environment. Overwrite it?",
                                         abort=True)
    mock_get_dev_env_descriptor_from_user.assert_not_called()
