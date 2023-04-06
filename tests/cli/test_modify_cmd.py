"""Tests for the modify command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal
from rich.console import Console
import io

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.modify_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.modify_cmd.DevEnvLocalSetup")
def test_execute_invalid_name(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_json):
    # Test setup
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock(DevEnvLocalSetup)
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = None
    test_dev_env_name =  "not existing env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

    console = Console(file=io.StringIO())
    console.print("[red]The Development Environment doesn't exist.")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.modify_cmd.get_confirm_from_user")
@patch("dem.cli.command.modify_cmd.get_modifications_from_user")
@patch("dem.cli.command.modify_cmd.data_management.write_deserialized_dev_env_json")
@patch("dem.cli.command.modify_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.modify_cmd.DevEnvLocalSetup")
def test_execute_valid_name(mock_DevEnvLocalSetup, mock_read_deserialized_dev_env_json,
                            mock_write_deserialized_dev_env_json, mock_get_modifications_from_user,
                            mock_get_confirm_from_user):
    # Test setup
    fake_deserialized_local_dev_env = MagicMock()
    mock_read_deserialized_dev_env_json.return_value = fake_deserialized_local_dev_env
    fake_dev_env_local_setup = MagicMock(DevEnvLocalSetup)
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup
    fake_dev_env = MagicMock(DevEnvLocal)
    fake_dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env
    fake_dev_env_local_setup.get_deserialized.return_value = fake_deserialized_local_dev_env
    test_dev_env_name =  "test"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_get_modifications_from_user.assert_called_once_with(fake_dev_env)
    mock_get_confirm_from_user.assert_called_once()
    fake_dev_env_local_setup.get_deserialized.assert_called_once()
    mock_write_deserialized_dev_env_json.assert_called_once_with(fake_deserialized_local_dev_env)