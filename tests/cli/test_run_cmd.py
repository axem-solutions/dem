"""Tests for the run CLI command."""
# tests/cli/test_run_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.run_cmd as run_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

import typer

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
@patch("dem.cli.command.run_cmd.stderr.print")
def test_handle_invalid_dev_env(mock_stderr_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None
    test_dev_env_name = "test_dev_env_name"

    # Run unit under test
    with pytest.raises(typer.Abort):
        # execute() gets tested directly to see if the exception is raised
        run_cmd.execute(mock_platform, test_dev_env_name, [])

        # Check expectations
        mock_stderr_print.assert_called_once_with("[red]Error: Unknown Development Environment: " + test_dev_env_name + "[/]")

        mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)


@patch("dem.cli.command.run_cmd.typer.confirm")
@patch("dem.cli.command.run_cmd.stderr.print")
def test_handle_missing_tool_images_no_fix(mock_stderr_print, mock_confirm):
    # Test setup
    test_missing_tool_images = {
        "missing_tool_image_1",
        "missing_tool_image_2",
        "missing_tool_image_3",
    }
    mock_dev_env_local = MagicMock()
    mock_platform = MagicMock()
    mock_confirm.side_effect = Exception()

    # Run unit under test
    # The exception doesn't metter, only the fact that the function execution has stopped.
    with pytest.raises(Exception):
        run_cmd.handle_missing_tool_images(test_missing_tool_images, mock_dev_env_local, 
                                           mock_platform)

        # Check expectations
        calls = [
            call("[red]Error: The following tool images are not available locally:[/]")
        ]
        for missing_tool_image in test_missing_tool_images:
            calls.append(call("[red]" + missing_tool_image + "[/]"))
        mock_stderr_print.assert_has_calls(calls)
        mock_confirm.assert_called_once_with("Should DEM try to fix the faulty Development Environment?", abort=True)

@patch("dem.cli.command.run_cmd.stdout.print")
@patch("dem.cli.command.run_cmd.typer.confirm")
@patch("dem.cli.command.run_cmd.stderr.print")
def test_handle_missing_tool_images_do_fix(mock_stderr_print, mock_confirm, mock_stdout_print):
    # Test setup
    test_missing_tool_images = {
        "missing_tool_image_1",
        "missing_tool_image_2",
        "missing_tool_image_3",
    }
    mock_dev_env_local = MagicMock()
    mock_platform = MagicMock()

    # Run unit under test
    run_cmd.handle_missing_tool_images(test_missing_tool_images, mock_dev_env_local, 
                                       mock_platform)

    # Check expectations
    calls = [
        call("[red]Error: The following tool images are not available locally:[/]")
    ]
    for missing_tool_image in test_missing_tool_images:
        calls.append(call("[red]" + missing_tool_image + "[/]"))
    mock_stderr_print.assert_has_calls(calls)
    mock_confirm.assert_called_once_with("Should DEM try to fix the faulty Development Environment?", abort=True)
    mock_platform.install_dev_env.assert_called_once_with(mock_dev_env_local)
    mock_stdout_print.assert_called_once_with("[green]DEM fixed the " + mock_dev_env_local.name + "![/]")

@patch("dem.cli.command.run_cmd.handle_missing_tool_images")
def test_execute(mock_handle_missing_tool_images):
    # Test setup
    test_dev_env_name = "test_dev_env_name"
    test_tool_type = "test_tool_type"
    test_workspace_path = "test_workspace_path"
    test_command = "test_command"
    test_args = ["run", test_dev_env_name, test_tool_type, test_workspace_path, test_command]
    
    mock_platform = MagicMock()
    mock_platform.tool_images.local.elements = ["test_image_name:test_image_version"]
    main.platform = mock_platform
    mock_dev_env_local = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env_local

    main.Platform.update_tool_images_on_instantiation = True

    mock_dev_env_local.tools = [
        {
            "image_name": "test_image_name",
            "image_version": "test_image_version",
            "type": test_tool_type
        },
        {
            "image_name": "missing_image_name",
            "image_version": "missing_image_version",
            "type": "missing_tool_type"
        },
    ]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, test_args, color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    assert main.Platform.update_tool_images_on_instantiation is False

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_platform.tool_images.local.update.assert_called_once()

    expected_missing_tool_image = {"missing_image_name:missing_image_version"}
    mock_handle_missing_tool_images.assert_called_once_with(expected_missing_tool_image, 
                                                            mock_dev_env_local, 
                                                            mock_platform)
    mock_platform.container_engine.run.assert_called_once_with(test_args[2:])