"""Tests for the list_host CLI command."""
# tests/cli/test_list_host_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.core.commands.list_host_cmd.Table")
@patch("dem.core.commands.list_host_cmd.stdout.print")
def test_list_host(mock_stdout_print: MagicMock, mock_Table: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    test_hosts = [
        {
            "name": "test_name1",
            "address": "test_url1"
        }
    ]
    mock_platform.hosts.list_host_configs.return_value = test_hosts
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-host"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_Table.assert_called_once()
    calls = [call("name"), call("address")]
    mock_table.add_column.assert_has_calls(calls)

    mock_platform.hosts.list_host_configs.assert_called_once()
    
    calls = []
    for host in test_hosts:
        calls.append(call(host["name"], host["address"]))

    mock_table.add_row.assert_has_calls(calls)

    mock_stdout_print.assert_called_once_with(mock_table)

@patch("dem.core.commands.list_host_cmd.Table")
@patch("dem.core.commands.list_host_cmd.stdout.print")
def test_list_host_non_available(mock_stdout_print: MagicMock, mock_Table: MagicMock):

    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_platform.hosts.list_host_configs.return_value = []
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-host"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_Table.assert_called_once()
    calls = [call("name"), call("address")]
    mock_table.add_column.assert_has_calls(calls)

    mock_platform.hosts.list_host_configs.assert_called_once()
    
    mock_stdout_print.assert_called_once_with("[yellow]No available remote hosts![/]")