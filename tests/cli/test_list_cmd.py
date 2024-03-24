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

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases

## Test listing the local dev envs.

@patch("dem.cli.command.list_cmd.stdout.print")
@patch("dem.cli.command.list_cmd.get_local_dev_env_status")
@patch("dem.cli.command.list_cmd.Table")
def test_with_valid_dev_env_json(mock_Table: MagicMock, mock_get_local_dev_env_status: MagicMock,
                                 mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    expected_dev_env_list = [
        ["demo", "Installed."],
        ["nagy_cica_project", "[red]Error: Required image is not available![/]"]
    ]
    fake_dev_envs = []
    for expected_dev_env in expected_dev_env_list:
        fake_dev_env = MagicMock()
        fake_dev_env.name = expected_dev_env[0]
        fake_dev_envs.append(fake_dev_env)
    mock_platform.local_dev_envs = fake_dev_envs
    main.platform = mock_platform

    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    mock_get_local_dev_env_status.side_effect = [
        expected_dev_env_list[0][1],
        expected_dev_env_list[1][1]
    ]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_Table.assert_called_once()
    mock_table.add_column.assert_has_calls([call("Development Environment"), call("Status")])
    mock_table.add_row.assert_has_calls([call(*(expected_dev_env_list[0])), 
                                         call(*(expected_dev_env_list[1]))])
    mock_stdout_print.assert_called_once_with(mock_table)

def test_with_empty_dev_env_json():
    # Test setup
    mock_platform = MagicMock()
    mock_platform.local_dev_envs = []
    main.platform = mock_platform

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
def test_without_avialable_catalogs(mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_platform.dev_env_catalogs.catalogs = []
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_stdout_print.assert_called_once_with("[yellow]No Development Environment Catalogs are available!")

def test_with_empty_catalog():
    # Test setup
    mock_catalog = MagicMock()
    mock_catalog.dev_envs = []
    mock_platform = MagicMock()
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No Development Environments are available in the catalogs.[/]")
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.list_cmd.get_catalog_dev_env_status")
def test_with_valid_dev_env_org_json(mock_get_catalog_dev_env_status: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    expected_dev_env_list = [
        ["org_only_env", "Ready to be installed."],
        ["demo", "Installed locally."],
        ["nagy_cica_project", "Incomplete local install. The missing images are available in the registry. Use `dem pull` to reinstall."],
        ["unavailable_image_env", "[red]Error: Required image is not available in the registry![/]"]
    ]
    fake_catalog_dev_envs = []
    for expected_dev_env in expected_dev_env_list:
        fake_dev_env = MagicMock()
        fake_dev_env.name = expected_dev_env[0]
        fake_catalog_dev_envs.append(fake_dev_env)
    mock_catalog = MagicMock()
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]
    mock_catalog.dev_envs = fake_catalog_dev_envs
    mock_platform.get_dev_env_by_name.side_effect = [None, MagicMock(), MagicMock()]

    mock_get_catalog_dev_env_status.side_effect = [
        expected_dev_env_list[0][1],
        expected_dev_env_list[1][1],
        expected_dev_env_list[2][1],
        expected_dev_env_list[3][1]
    ]

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    calls = []
    for fake_dev_env in fake_catalog_dev_envs:
        calls.append(call(fake_dev_env))
    mock_platform.get_dev_env_by_name.has_calls(calls)

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

def test_local_tool_images():
    # Test setup
    test_local_tool_images = [
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest",
        "axemsolutions/make_gnu_arm:latest",
    ]
    mock_platform = MagicMock()
    mock_platform.container_engine.get_local_tool_images.return_value = test_local_tool_images
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.container_engine.get_local_tool_images.assert_called_once()

    expected_table = Table()
    expected_table.add_column("Repository")
    expected_table.add_row("axemsolutions/cpputest:latest")
    expected_table.add_row("axemsolutions/stlink_org:latest")
    expected_table.add_row("axemsolutions/make_gnu_arm:latest")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

def test_no_local_tool_images():
    # Test setup
    test_local_tool_images = []
    mock_platform = MagicMock()
    mock_platform.container_engine.get_local_tool_images.return_value = test_local_tool_images
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.container_engine.get_local_tool_images.assert_called_once()
    
    expected_table = Table()
    expected_table.add_column("Repository")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

## Test listing the local tool images.

def test_registry_tool_images():
    # Test setup
    test_registry_tool_images = [
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest",
        "axemsolutions/make_gnu_arm:latest",
    ]
    mock_platform = MagicMock()
    mock_platform.registries.list_repos.return_value = test_registry_tool_images
    main.platform = mock_platform

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
def test_empty_repository(mock_stdout_print: MagicMock):
    # Test setup
    test_registry_tool_images = []
    mock_platform = MagicMock()
    mock_platform.registries.list_repos.return_value = test_registry_tool_images
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.registries.list_repos.assert_called_once()
    mock_stdout_print.assert_called_once_with("[yellow]No images are available in the registries!")

@patch("dem.cli.command.list_cmd.stdout.print")
def test_no_registries_available(mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_platform.registries.registries = []
    main.platform = mock_platform

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_stdout_print.assert_called_once_with("[yellow]No registries are available!")