"""Unit tests for the list CLI command."""
# tests/cli/test_list_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import io
from rich.console import Console
from rich.table import Table
import json
import tests.fake_data as fake_data

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases

## Test listing the local dev envs.

@patch("dem.cli.command.list_cmd.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.command.list_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.list_cmd.registry.list_repos")
def test_with_valid_dev_env_json(mock_list_repos, mock_ContainerEngine,
                                 mock_get_deserialized_dev_env_json):
    # Test setup
    test_local_images = [
        "alpine:latest",
        "make_gnu_arm:v1.0.0",
        "stlink_org:latest", 
        "stlink_org:v1.0.0",
        "cpputest:latest",
        "make_gnu_arm:latest", 
        "make_gnu_arm:v0.1.0", 
        "make_gnu_arm:v1.1.0",
        "debian:latest",
        "ubuntu:latest",
        "hello-world:latest",
    ]
    test_registry_images = [
        "make_gnu_arm:latest", 
        "cpputest:latest",
        "stlink_org:latest", 
    ]
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_image_tags.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    # Check expectations
    mock_get_deserialized_dev_env_json.assert_called_once()
    mock_container_engine.get_local_image_tags.assert_called_once()
    mock_list_repos.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_table = Table()
    expected_table.add_column("Development Environment")
    expected_table.add_column("Status")
    expected_table.add_row("demo", "Installed.")
    expected_table.add_row("nagy_cica_project", "[red]Error: Required image is not available![/]")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stdout

@patch("dem.cli.command.list_cmd.data_management.get_deserialized_dev_env_json")
def test_with_empty_dev_env_json(mock_get_deserialized_dev_env_json):
    # Test setup
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.empty_dev_env_json)

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    # Check expectations
    mock_get_deserialized_dev_env_json.assert_called_once()

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No installed Development Environments.[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stdout

## Test listing the org dev envs.

@patch("dem.cli.command.list_cmd.data_management.get_deserialized_dev_env_org_json")
def test_with_empty_dev_env_org_json(mock_get_deserialized_dev_env_org_json):
    # Test setup
    mock_get_deserialized_dev_env_org_json.return_value = json.loads(fake_data.empty_dev_env_org_json)

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    mock_get_deserialized_dev_env_org_json.assert_called_once()

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No Development Environment in your organization.[/]")
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.list_cmd.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.command.list_cmd.data_management.get_deserialized_dev_env_org_json")
@patch("dem.cli.command.list_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.list_cmd.registry.list_repos")
def test_with_valid_dev_env_org_json(mock_list_repos, mock_ContainerEngine, 
                                     mock_get_deserialized_dev_env_org_json,
                                     mock_get_deserialized_dev_env_json):
    # Test setup
    test_local_images = [
        "alpine:latest",
        "make_gnu_arm:v1.0.0",
        "stlink_org:latest", 
        "stlink_org:v1.0.0",
        "cpputest:latest",
        "make_gnu_arm:latest", 
        "make_gnu_arm:v0.1.0", 
        "make_gnu_arm:v1.1.0",
        "debian:latest",
        "ubuntu:latest",
        "hello-world:latest",
    ]
    test_registry_images = [
        "make_gnu_arm:latest", 
        "cpputest:latest",
        "stlink_org:latest", 
        "cmake:latest",
        "llvm:latest",
        "pemicro:latest",
        "unity:latest",
        "bazel:latest",
        "gnu_arm:latest",
        "jlink:latest",
    ]
    mock_get_deserialized_dev_env_org_json.return_value = json.loads(fake_data.dev_env_org_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_image_tags.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    mock_get_deserialized_dev_env_org_json.assert_called_once()

    expected_table = Table()
    expected_table.add_column("Development Environment")
    expected_table.add_column("Status")
    expected_table.add_row("org_only_env", "Ready to be installed.")
    expected_table.add_row("demo", "Installed locally.")
    expected_table.add_row("nagy_cica_project", "Incomplete local install. Reinstall needed.")
    expected_table.add_row("unavailable_image_env", "[red]Error: Required image is not available in the registry![/]")
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
    console.print("[red]Error: This command is not supported.[/]")
    assert console.file.getvalue() == runner_result.stderr