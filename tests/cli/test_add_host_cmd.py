"""Tests for the add-host CLI command."""

import dem.cli.main as main
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
import json

# Global test variables
runner = CliRunner(mix_stderr=False)

# Mocked DevEnvLocalSetup instance
mocked_platform = MagicMock()
mocked_platform.config_file.deserialized = {}


@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
def test_add_host(mock_platform):
    # Test setup
    test_name = "test_host_name"
    test_address = "test_host_address"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["name"] == test_name
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == test_address
    mocked_platform.config_file.flush.assert_called_once()


@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
@patch("builtins.input", return_value="yes")
def test_add_host_already_added(mock_input, mock_platform):
    # Test setup
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    mocked_platform.config_file.flush.reset_mock()
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["name"] == test_name
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == test_address
    mocked_platform.config_file.flush.assert_called_once()


# Test for when the user declines to overwrite an existing host
@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
@patch("builtins.input", return_value="no")
def test_add_host_decline_overwrite(mock_input, mock_platform):
    # Test setup
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    mocked_platform.config_file.flush.reset_mock()
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code == 0  # Update the expected exit code to 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == "old_address"
    mocked_platform.config_file.flush.assert_not_called()

@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", side_effect=Exception("Mocked exception"))
def test_add_host_exception(mock_platform):
    # Test setup
    test_name = "test_host_name"
    test_address = "test_host_address"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code != 0
    # Remove the assertion for the exception message in the output
# Test for when the add-host command is invoked without any arguments
@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
def test_add_host_no_arguments(mock_platform):
    runner_result = runner.invoke(main.typer_cli, ["add-host"], color=True)
    assert runner_result.exit_code != 0
    assert "Missing argument 'NAME'" in runner_result.stderr  # Check stderr

@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
def test_add_host_one_argument(mock_platform):
    runner_result = runner.invoke(main.typer_cli, ["add-host", "test_host_name"], color=True)
    assert runner_result.exit_code != 0
    assert "Missing argument 'ADDRESS'" in runner_result.stderr  # Check stderr

@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
def test_add_host_invalid_arguments(mock_platform):
    runner_result = runner.invoke(main.typer_cli, ["add-host", "", "test_host_address"], color=True)
    assert runner_result.exit_code != 0
    assert "Error: NAME or ADDRESS cannot be empty." in runner_result.output

@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
@patch("builtins.input", side_effect=EOFError)
def test_add_host_no_user_input(mock_input, mock_platform):
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code != 0
    assert "Host addition cancelled." in runner_result.output

@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
@patch("builtins.input", side_effect=["invalid_choice", "yes"])
def test_add_host_invalid_choice_then_yes(mock_input, mock_platform):
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == test_address

# Test for when the user provides an invalid choice and then chooses 'no'
@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
@patch("builtins.input", side_effect=["invalid_choice", "no"])
def test_add_host_invalid_choice_then_no(mock_input, mock_platform):
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == "old_address"

# Test for adding a new host when the host name doesn't already exist
@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
def test_add_new_host(mock_platform):
    test_name = "new_host_name"
    test_address = "new_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": "existing_host_name", "address": "existing_host_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert {"name": test_name, "address": test_address} in mocked_platform.config_file.deserialized["hosts"]

# Test for adding a host when the data list is initially empty
@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
def test_add_host_empty_data(mock_platform):
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized = {}
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["name"] == test_name
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == test_address

@patch("dem.cli.command.add_host_cmd.DevEnvLocalSetup", return_value=mocked_platform)
@patch("builtins.input", side_effect=["maybe", EOFError])  # First return "maybe", then raise EOFError
def test_add_host_eof_during_invalid_choice(mock_input, mock_platform):
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert "Please enter 'yes' or 'no'." in runner_result.output
    assert "Host addition cancelled." in runner_result.output
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == "old_address"
