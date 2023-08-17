"""Tests for the list_reg CLI command."""
# tests/cli/test_list_reg_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.cli.command.list_reg_cmd.Table")
@patch("dem.cli.command.list_reg_cmd.stdout.print")
@patch("dem.cli.command.list_reg_cmd.DevEnvLocalSetup")
def test_list_reg(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock, 
                  mock_Table: MagicMock):
    # Test setup
    mock_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_local_platform
    test_registries = [
        {
            "name": "test_name1",
            "url": "test_url1"
        },
        {
            "name": "test_name2",
            "url": "test_url2"
        },
    ]
    mock_local_platform.registries.list_registries.return_value = test_registries
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-reg"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_DevEnvLocalSetup.assert_called_once()

    mock_Table.assert_called_once()
    calls = [call("name"), call("url")]
    mock_table.add_column.assert_has_calls(calls)

    mock_local_platform.registries.list_registries.assert_called_once()
    
    calls = []
    for registry in test_registries:
        calls.append(call(registry["name"], registry["url"]))
    mock_table.add_row.assert_has_calls(calls)

    mock_stdout_print.assert_called_once_with(mock_table)

@patch("dem.cli.command.list_reg_cmd.Table")
@patch("dem.cli.command.list_reg_cmd.stdout.print")
@patch("dem.cli.command.list_reg_cmd.DevEnvLocalSetup")
def test_list_reg_non_available(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock, 
                                mock_Table):
    # Test setup
    mock_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_local_platform
    mock_local_platform.registries.list_registries.return_value = []
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list-reg"], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_DevEnvLocalSetup.assert_called_once()

    mock_Table.assert_called_once()
    calls = [call("name"), call("url")]
    mock_table.add_column.assert_has_calls(calls)

    mock_local_platform.registries.list_registries.assert_called_once()
    
    mock_stdout_print.assert_called_once_with("[yellow]No available registries![/]")