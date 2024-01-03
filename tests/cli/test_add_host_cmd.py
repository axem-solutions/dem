"""Tests for the add-host CLI command."""

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from click.testing import Result
import pytest

# Global test variables
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.add_host_cmd.stdout.print")
def test_add_host(mock_print: MagicMock) -> None:
    # Test setup
    mocked_platform = MagicMock()
    mocked_platform.hosts.list_host_configs.return_value = {}
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"

    # Run unit under test
    runner_result: Result = runner.invoke(main.typer_cli, 
                                          ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mocked_platform.hosts.add_host.assert_called_once_with({"name": test_name, "address": test_address})
    mock_print.assert_called_once_with("[green]Host added successfully![/]")

@patch("dem.cli.command.add_host_cmd.stdout.print")
@patch("dem.cli.command.add_host_cmd.typer.confirm")
def test_add_host_already_added(mock_confirm: MagicMock, mock_print: MagicMock) -> None:
    # Test setup
    mocked_platform = MagicMock()
    main.platform = mocked_platform
    test_name = "test_host_name"
    test_address = "test_host_address"
    mocked_platform.hosts.list_host_configs.return_value = [{"name": test_name, 
                                                             "address": "old_address"}]

    # Run unit under test
    runner_result: Result = runner.invoke(main.typer_cli, 
                                          ["add-host", test_name, test_address], color=True)

    # Check expectations
    assert runner_result.exit_code == 0
    
    mock_confirm.assert_called_once_with(f"Host with name {test_name} already exists. Do you want to overwrite it?",
                                         abort=True)
    mocked_platform.hosts.delete_host.assert_called_once_with({"name": test_name,
                                                                "address": "old_address"})
    mocked_platform.hosts.add_host.assert_called_once_with({"name": test_name, "address": test_address})
    mock_print.assert_called_once_with("[green]Host added successfully![/]")

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
    with pytest.raises(Exception):
        runner_result = runner.invoke(main.typer_cli, ["add-host", "", "test_host_address"], color=True)
        assert runner_result.exit_code != 0
        assert "Error: NAME or ADDRESS cannot be empty." in runner_result.output