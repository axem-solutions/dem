"""Tests for the del-host CLI command."""
# tests/cli/test_del_host_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call
from click.testing import Result

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.core.commands.del_host_cmd.stdout.print")
def test_del_host_cmd(mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_host_config: dict[str, str] = {
        "name": "test_name",
        "address": "test_address"
    }
    mock_platform.hosts.list_host_configs.return_value = [test_host_config]

    # Run unit under test
    runner_result: Result = runner.invoke(main.typer_cli, ["del-host", test_host_config["name"]], 
                                          color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.hosts.delete_host.assert_called_once_with(test_host_config)
    mock_stdout_print.assert_called_once_with("[green]Host deleted successfully![/]")

@patch("dem.core.commands.del_host_cmd.stderr.print")
def test_del_host_cmd_not_existing(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_host_config: dict[str, str] = {
        "name": "test_name",
        "address": "test_address"
    }
    mock_platform.hosts.list_host_configs.return_value = [test_host_config]

    # Run unit under test
    runner_result: Result = runner.invoke(main.typer_cli, ["del-host", "not_existing_name"], 
                                          color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.hosts.delete_host.assert_not_called()
    mock_stderr_print.assert_called_once_with("[red]Error: The input Host does not exist.[/]")