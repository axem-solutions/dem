"""Tests for the add-host CLI command."""

import dem.cli.main as main
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
import json

# Global test variables
runner = CliRunner(mix_stderr=False)

# Mocked DevEnvLocalSetup instance

def test_add_host():
    # Test setup
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["name"] == test_name
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == test_address
    mocked_platform.config_file.flush.assert_called_once()

@patch("builtins.input", return_value="yes")
def test_add_host_already_added(mock_input):
    # Test setup
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
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
@patch("builtins.input", return_value="no")
def test_add_host_decline_overwrite(mock_input):
    # Test setup
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    mocked_platform.config_file.flush.reset_mock()
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code == 0  # Update the expected exit code to 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == "old_address"
    mocked_platform.config_file.flush.assert_not_called()

def test_add_host_exception():
    # Test setup
    test_name = "test_host_name"
    test_address = "test_host_address"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code != 0

# Test for when the add-host command is invoked without any arguments
def test_add_host_no_arguments():
    runner_result = runner.invoke(main.typer_cli, ["add-host"], color=True)
    assert runner_result.exit_code != 0
    assert "Missing argument 'NAME'" in runner_result.stderr  # Check stderr

def test_add_host_one_argument():
    runner_result = runner.invoke(main.typer_cli, ["add-host", "test_host_name"], color=True)
    assert runner_result.exit_code != 0
    assert "Missing argument 'ADDRESS'" in runner_result.stderr  # Check stderr

def test_add_host_invalid_arguments():
    runner_result = runner.invoke(main.typer_cli, ["add-host", "", "test_host_address"], color=True)
    assert runner_result.exit_code != 0
    assert "Error: NAME or ADDRESS cannot be empty." in runner_result.output

@patch("builtins.input", side_effect=EOFError)
def test_add_host_no_user_input(mock_input):
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code != 0
    assert "Host addition cancelled." in runner_result.output

@patch("builtins.input", side_effect=["invalid_choice", "yes"])
def test_add_host_invalid_choice_then_yes(mock_input):
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == test_address

# Test for when the user provides an invalid choice and then chooses 'no'
@patch("builtins.input", side_effect=["invalid_choice", "no"])
def test_add_host_invalid_choice_then_no(mock_input):
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == "old_address"

# Test for adding a new host when the host name doesn't already exist
def test_add_new_host():
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
    test_name = "new_host_name"
    test_address = "new_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": "existing_host_name", "address": "existing_host_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert {"name": test_name, "address": test_address} in mocked_platform.config_file.deserialized["hosts"]

# Test for adding a host when the data list is initially empty
def test_add_host_empty_data():
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized = {}
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert mocked_platform.config_file.deserialized["hosts"][0]["name"] == test_name
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == test_address

@patch("builtins.input", side_effect=["maybe", EOFError])  # First return "maybe", then raise EOFError
def test_add_host_eof_during_invalid_choice(mock_input):
    mocked_platform = MagicMock()
    mocked_platform.config_file.deserialized = {}
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.config_file.deserialized["hosts"] = [{"name": test_name, "address": "old_address"}]
    runner_result = runner.invoke(main.typer_cli, ["add-host", test_name, test_address], color=True)
    assert runner_result.exit_code == 0
    assert "Please enter 'yes' or 'no'." in runner_result.output
    assert "Host addition cancelled." in runner_result.output
    assert mocked_platform.config_file.deserialized["hosts"][0]["address"] == "old_address"
