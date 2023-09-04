"""Unit tests for the list CLI command."""
# tests/cli/test_list_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.list_cmd as list_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

import io
from rich.console import Console
from rich.table import Table
import json
import tests.fake_data as fake_data
from dem.core.dev_env import DevEnv, DevEnv
from dem.core.tool_images import ToolImages

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases

## Test listing the local dev envs.

@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_with_valid_dev_env_json(mock_DevEnvLocalSetup: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    expected_dev_env_list = [
        ["demo", "Installed."],
        ["nagy_cica_project", "[red]Error: Required image is not available![/]"]
    ]
    fake_image_statuses = [
        [ToolImages.LOCAL_AND_REGISTRY] * 5,
        [ToolImages.NOT_AVAILABLE] * 5
    ]
    fake_dev_envs = []
    for idx, expected_dev_env in enumerate(expected_dev_env_list):
        fake_dev_env = MagicMock(spec=DevEnv)
        fake_dev_env.name = expected_dev_env[0]
        fake_dev_env.check_image_availability.return_value = fake_image_statuses[idx]
        fake_dev_envs.append(fake_dev_env)
    mock_platform.local_dev_envs = fake_dev_envs
    mock_DevEnvLocalSetup.return_value = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    # Check expectations
    mock_DevEnvLocalSetup.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_table = Table()
    expected_table.add_column("Development Environment")
    expected_table.add_column("Status")
    expected_table.add_row(*expected_dev_env_list[0])
    expected_table.add_row(*expected_dev_env_list[1])
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stdout

@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_with_empty_dev_env_json(mock_DevEnvLocalSetup):
    # Test setup
    mock_platform = MagicMock()
    mock_platform.local_dev_envs = []
    mock_DevEnvLocalSetup.return_value = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No installed Development Environments.[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stdout

## Test listing the org dev envs.

@patch("dem.cli.command.list_cmd.stdout.print")
@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_without_avialable_catalogs(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.dev_env_catalogs.catalogs = []

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    mock_stdout_print.assert_called_once_with("[yellow]No Development Environment Catalogs are available!")

@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_with_empty_catalog(mock_DevEnvLocalSetup: MagicMock):
    # Test setup
    mock_catalog = MagicMock()
    mock_catalog.dev_envs = []
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()

    console = Console(file=io.StringIO())
    console.print("[yellow]No Development Environments are available in the catalogs.[/]")
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_with_valid_dev_env_org_json(mock_DevEnvLocalSetup):
    # Test setup
    mock_platform = MagicMock()
    expected_dev_env_list = [
        ["org_only_env", "Ready to be installed."],
        ["demo", "Installed locally."],
        ["nagy_cica_project", "Incomplete local install. Reinstall needed."],
        ["unavailable_image_env", "[red]Error: Required image is not available in the registry![/]"]
    ]
    fake_image_statuses = [
        [ToolImages.REGISTRY_ONLY] * 5,
        [ToolImages.LOCAL_AND_REGISTRY] * 6,
        [ToolImages.LOCAL_AND_REGISTRY, ToolImages.REGISTRY_ONLY],
        [ToolImages.NOT_AVAILABLE] * 4
    ]
    fake_catalog_dev_envs = []
    for idx, expected_dev_env in enumerate(expected_dev_env_list):
        fake_dev_env = MagicMock(spec=DevEnv)
        fake_dev_env.name = expected_dev_env[0]
        fake_dev_env.check_image_availability.return_value = fake_image_statuses[idx]
        fake_catalog_dev_envs.append(fake_dev_env)
    mock_catalog = MagicMock()
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]
    mock_catalog.dev_envs = fake_catalog_dev_envs
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.get_local_dev_env.side_effect = [None, MagicMock(), MagicMock()]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    mock_DevEnvLocalSetup.assert_called_once()
    calls = []
    for fake_dev_env in fake_catalog_dev_envs:
        calls.append(call(fake_dev_env))
    mock_platform.get_local_dev_env.has_calls(calls)

    expected_table = Table()
    expected_table.add_column("Development Environment")
    expected_table.add_column("Status")
    for expected_dev_env in expected_dev_env_list:
        expected_table.add_row(*expected_dev_env)
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

def test_without_options():
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list"], color=True)
    
    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print(\
"""Usage: dem list [OPTIONS]
Try 'dem list --help' for help.

Error: You need to set the scope and what to list!""")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stderr

def test_with_invalid_option():
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--all", "--env"], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: Invalid options.[/]")
    assert console.file.getvalue() == runner_result.stderr

## Test listing the local tool images.

@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_local_tool_images(mock_DevEnvLocalSetup: MagicMock):
    # Test setup
    test_local_tool_images = [
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest",
        "axemsolutions/make_gnu_arm:latest",
    ]
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.container_engine.get_local_tool_images.return_value = test_local_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    mock_platform.container_engine.get_local_tool_images.assert_called_once()

    expected_table = Table()
    expected_table.add_column("Repository")
    expected_table.add_row("axemsolutions/cpputest:latest")
    expected_table.add_row("axemsolutions/stlink_org:latest")
    expected_table.add_row("axemsolutions/make_gnu_arm:latest")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_no_local_tool_images(mock_DevEnvLocalSetup: MagicMock):
    # Test setup
    test_local_tool_images = []
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.container_engine.get_local_tool_images.return_value = test_local_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    mock_platform.container_engine.get_local_tool_images.assert_called_once()
    
    expected_table = Table()
    expected_table.add_column("Repository")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

## Test listing the local tool images.

@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_registry_tool_images(mock_DevEnvLocalSetup: MagicMock):
    # Test setup
    test_registry_tool_images = [
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest",
        "axemsolutions/make_gnu_arm:latest",
    ]
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.registries.list_repos.return_value = test_registry_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.registries.list_repos.assert_called_once()
    
    expected_table = Table()
    expected_table.add_column("Repository")
    expected_table.add_row("axemsolutions/cpputest:latest")
    expected_table.add_row("axemsolutions/stlink_org:latest")
    expected_table.add_row("axemsolutions/make_gnu_arm:latest")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.list_cmd.stdout.print")
@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_empty_repository(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock):
    # Test setup
    test_registry_tool_images = []
    mock_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = mock_platform
    mock_platform.registries.list_repos.return_value = test_registry_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.registries.list_repos.assert_called_once()
    mock_stdout_print.assert_called_once_with("[yellow]No images are available in the registries!")

@patch("dem.cli.command.list_cmd.stdout.print")
@patch("dem.cli.command.list_cmd.DevEnvLocalSetup")
def test_no_registries_available(mock_DevEnvLocalSetup: MagicMock, mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_platform.registries.registries = []
    mock_DevEnvLocalSetup.return_value = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_DevEnvLocalSetup.assert_called_once()
    mock_stdout_print.assert_called_once_with("[yellow]No registries are available!")

def test_get_local_dev_env_status_reinstall():
    # Test setup
    mock_dev_env = MagicMock()
    mock_tool_images = MagicMock()

    mock_dev_env.check_image_availability.return_value = [list_cmd.ToolImages.REGISTRY_ONLY]

    # Run unit under test
    actual_dev_env_status = list_cmd.get_local_dev_env_status(mock_dev_env, mock_tool_images)

    # Check expectations
    assert actual_dev_env_status is list_cmd.dev_env_local_status_messages[list_cmd.DEV_ENV_LOCAL_REINSTALL]