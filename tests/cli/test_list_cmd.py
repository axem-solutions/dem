"""Unit tests for the list CLI command."""
# tests/cli/test_list_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.list_cmd as list_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import io
from rich.console import Console
from rich.table import Table
import json
import tests.fake_data as fake_data
from dem.core.dev_env_setup import DevEnvLocal, DevEnvOrg
from dem.core.tool_images import ToolImages

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
def test_is_dev_env_org_installed_locally_true(mock_DevEnvLocalSetup):
    # Test setup
    fake_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_local_platform

    fake_dev_env_org = MagicMock()
    fake_dev_env_org.get_local_instance.return_value = MagicMock()

    # Run unit under test
    actual_is_installed = list_cmd.is_dev_env_org_installed_locally(fake_dev_env_org)

    # Check expectations
    assert actual_is_installed is True

    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_org.get_local_instance.assert_called_once_with(fake_local_platform)

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
def test_is_dev_env_org_installed_locally_false(mock_DevEnvLocalSetup):
    # Test setup
    fake_local_platform = MagicMock()
    mock_DevEnvLocalSetup.return_value = fake_local_platform

    fake_dev_env_org = MagicMock()
    fake_dev_env_org.get_local_instance.return_value = None

    # Run unit under test
    actual_is_installed = list_cmd.is_dev_env_org_installed_locally(fake_dev_env_org)

    # Check expectations
    assert actual_is_installed is False

    mock_DevEnvLocalSetup.assert_called_once()
    fake_dev_env_org.get_local_instance.assert_called_once_with(fake_local_platform)

## Test listing the local dev envs.

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
def test_with_valid_dev_env_json(mock_DevEnvLocalSetup):
    # Test setup
    fake_local_platform = MagicMock()
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
        fake_dev_env = MagicMock(spec=DevEnvLocal)
        fake_dev_env.name = expected_dev_env[0]
        fake_dev_env.check_image_availability.return_value = fake_image_statuses[idx]
        fake_dev_envs.append(fake_dev_env)
    fake_local_platform.dev_envs = fake_dev_envs
    mock_DevEnvLocalSetup.return_value = fake_local_platform

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

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
def test_with_empty_dev_env_json(mock_DevEnvLocalSetup):
    # Test setup
    fake_dev_env_setup = MagicMock()
    fake_dev_env_setup.dev_envs = []
    mock_DevEnvLocalSetup.return_value = fake_dev_env_setup

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No installed Development Environments.[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stdout

## Test listing the org dev envs.

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvOrgSetup")
def test_with_empty_dev_env_org_json(mock_DevEnvOrgSetup):
    # Test setup
    fake_dev_env_org = MagicMock()
    fake_dev_env_org.dev_envs = []
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No Development Environment in your organization.[/]")
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.list_cmd.is_dev_env_org_installed_locally")
@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvOrgSetup")
def test_with_valid_dev_env_org_json(mock_DevEnvOrgSetup, mock_is_dev_env_org_installed_locally):
    # Test setup
    fake_dev_env_org_setup = MagicMock()
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
    fake_org_dev_envs = []
    for idx, expected_dev_env in enumerate(expected_dev_env_list):
        fake_dev_env = MagicMock(spec=DevEnvOrg)
        fake_dev_env.name = expected_dev_env[0]
        fake_dev_env.check_image_availability.return_value = fake_image_statuses[idx]
        fake_org_dev_envs.append(fake_dev_env)
    fake_dev_env_org_setup.dev_envs = fake_org_dev_envs
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup
    mock_is_dev_env_org_installed_locally.side_effect = [False, True, True]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    mock_DevEnvOrgSetup.assert_called_once()
    mock_is_dev_env_org_installed_locally.assert_called()

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

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
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

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
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

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
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

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
def test_empty_repository(mock_DevEnvLocalSetup: MagicMock):
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
    
    expected_table = Table()
    expected_table.add_column("Repository")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout
