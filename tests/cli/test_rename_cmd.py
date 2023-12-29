"""Tests for the rename CLI command."""
# tests/cli/test_rename_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
def test_rename_success():
    # Test setup
    original_dev_env_name = "original_dev_env_name"
    new_dev_env_name = "new_dev_env_name"

    fake_local_platform = MagicMock()
    main.platform = fake_local_platform
    
    fake_dev_env_to_rename = MagicMock()
    fake_local_platform.get_dev_env_by_name.return_value = fake_dev_env_to_rename

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, 
                                  ["rename", original_dev_env_name, new_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    assert fake_dev_env_to_rename.name is new_dev_env_name

    fake_local_platform.get_dev_env_by_name.assert_called_once_with(original_dev_env_name)
    fake_local_platform.flush_descriptors.assert_called_once()

@patch("dem.cli.command.rename_cmd.stderr.print")
def test_rename_non_existing(mock_stderr_print):
    # Test setup
    original_dev_env_name = "original_dev_env_name"
    new_dev_env_name = "new_dev_env_name"

    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, 
                                  ["rename", original_dev_env_name, new_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.get_dev_env_by_name.assert_called_once_with(original_dev_env_name)
    mock_stderr_print.assert_called_once_with("[red]Error: The input Development Environment does not exist.[/]")