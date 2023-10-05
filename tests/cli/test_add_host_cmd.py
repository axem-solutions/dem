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
