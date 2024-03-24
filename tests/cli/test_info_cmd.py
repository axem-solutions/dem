"""Unit tests for the info CLI command."""
# tests/cli/test_info_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.info_cmd as info_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import MagicMock, call, patch

import io
from rich.console import Console
from rich.table import Table
from dem.core.tool_images import ToolImages

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test helpers

def get_expected_table(expected_tools: list[list[str]]) ->str:
    expected_table = Table()
    expected_table.add_column("Type")
    expected_table.add_column("Image")
    expected_table.add_column("Status")
    for expected_tool in expected_tools:
        expected_table.add_row(*expected_tool)
    console = Console(file=io.StringIO())
    console.print(expected_table)
    return console.file.getvalue()

## Test cases

@patch("dem.cli.command.info_cmd.stdout.print")
@patch("dem.cli.command.info_cmd.Table")
def test_print_info(mock_Table: MagicMock, mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "axemsolutions/make_gnu_arm:latest"
    mock_tool_image1.availability = info_cmd.ToolImage.LOCAL_AND_REGISTRY

    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "axemsolutions/stlink_org:latest"
    mock_tool_image2.availability = info_cmd.ToolImage.LOCAL_ONLY

    mock_tool_image3 = MagicMock()
    mock_tool_image3.name = "axemsolutions/cpputest:latest"
    mock_tool_image3.availability = info_cmd.ToolImage.REGISTRY_ONLY

    mock_dev_env = MagicMock()
    mock_dev_env.tool_images = [ mock_tool_image1, mock_tool_image2, mock_tool_image3]
    
    # Run unit under test
    info_cmd.print_info(mock_dev_env)

    # Check expectations
    mock_table.add_column.assert_has_calls([
        call("Image"),
        call("Status")
    ])
    mock_table.add_row.assert_has_calls([
        call("axemsolutions/make_gnu_arm:latest", "Image is available locally and in the registry."),
        call("axemsolutions/stlink_org:latest", "Image is available locally."),
        call("axemsolutions/cpputest:latest", "Image is available in the registry."),
    ])
    mock_stdout_print.assert_called_once_with(mock_table)

@patch("dem.cli.command.info_cmd.stderr.print")
def test_execute_dev_env_not_found(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    mock_platform.dev_env_catalogs.catalogs = []

    test_dev_env_name = "test_dev_env_name"
    mock_platform.get_dev_env_by_name.return_value = None

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["info", test_dev_env_name], color=True)

    # Check expectations
    assert runner_result.exit_code == 0
    
    mock_platform.load_dev_envs.assert_called_once()
    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stderr_print.assert_called_once_with(f"[red]Error: Unknown Development Environment: {test_dev_env_name}[/]\n")

@patch("dem.cli.command.info_cmd.print_info")
def test_execute(mock_print_info: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    test_dev_env_name = "test_dev_env_name"
    mock_platform.get_dev_env_by_name.return_value = None

    mock_dev_env = MagicMock()

    mock_catalog = MagicMock()
    mock_catalog.get_dev_env_by_name.return_value = mock_dev_env
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["info", test_dev_env_name], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.load_dev_envs.assert_called_once()
    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_catalog.request_dev_envs.assert_called_once()
    mock_catalog.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_dev_env.assign_tool_image_instances.assert_called_once_with(mock_platform.tool_images)
    mock_print_info.assert_called_once_with(mock_dev_env)