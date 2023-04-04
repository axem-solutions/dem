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
import dem.core.dev_env_setup as dev_env_setup

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases

## Test listing the local dev envs.

@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
@patch("dem.cli.command.list_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.list_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.list_cmd.registry.list_repos")
def test_with_valid_dev_env_json(mock_list_repos, mock_ContainerEngine,
                                 mock_read_deserialized_dev_env_json, mock_DevEnvLocalSetup):
    # Test setup
    test_local_images = [
        "axemsolutions/make_gnu_arm:v1.0.0",
        "axemsolutions/stlink_org:latest", 
        "axemsolutions/stlink_org:v1.0.0",
        "axemsolutions/cpputest:latest",
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/make_gnu_arm:v0.1.0", 
        "axemsolutions/make_gnu_arm:v1.1.0",
    ]
    test_registry_images = [
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest", 
    ]
    fake_dev_env_json_deserialized = json.loads(fake_data.dev_env_json)
    mock_read_deserialized_dev_env_json.return_value = fake_dev_env_json_deserialized
    fake_dev_env_local_setup = MagicMock()
    fake_dev_envs = []
    for dev_env_descriptor in fake_dev_env_json_deserialized["development_environments"]:
        fake_dev_envs.append(dev_env_setup.DevEnvLocal(descriptor=dev_env_descriptor))
    fake_dev_env_local_setup.dev_envs = fake_dev_envs
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup

    fake_container_engine = MagicMock()
    fake_container_engine.get_local_tool_images.return_value = test_local_images
    mock_ContainerEngine.return_value = fake_container_engine
    mock_list_repos.return_value = test_registry_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    # Check expectations
    mock_read_deserialized_dev_env_json.assert_called_once()
    mock_DevEnvLocalSetup.assert_called_once_with(fake_dev_env_json_deserialized)
    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called_once()
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

@patch("dem.cli.command.list_cmd.data_management.read_deserialized_dev_env_json")
def test_with_empty_dev_env_json(mock_read_deserialized_dev_env_json):
    # Test setup
    mock_read_deserialized_dev_env_json.return_value = json.loads(fake_data.empty_dev_env_json)

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--env"])

    # Check expectations
    mock_read_deserialized_dev_env_json.assert_called_once()

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No installed Development Environments.[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stdout

## Test listing the org dev envs.

@patch("dem.cli.command.list_cmd.data_management.read_deserialized_dev_env_org_json")
def test_with_empty_dev_env_org_json(mock_read_deserialized_dev_env_org_json):
    # Test setup
    mock_read_deserialized_dev_env_org_json.return_value = json.loads(fake_data.empty_dev_env_org_json)

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    mock_read_deserialized_dev_env_org_json.assert_called_once()

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No Development Environment in your organization.[/]")
    assert console.file.getvalue() == runner_result.stdout

def mock_get_local_instance(dev_env_local_setup_obj: dev_env_setup.DevEnvLocalSetup) -> (dev_env_setup.DevEnvLocal | None):
    pass


@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvLocalSetup")
@patch("dem.cli.command.list_cmd.dev_env_setup.DevEnvOrgSetup")
@patch("dem.cli.command.list_cmd.data_management.read_deserialized_dev_env_org_json")
@patch("dem.cli.command.list_cmd.data_management.read_deserialized_dev_env_json")
@patch("dem.cli.command.list_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.list_cmd.registry.list_repos")
def test_with_valid_dev_env_org_json(mock_list_repos, mock_ContainerEngine, 
                                     mock_read_deserialized_dev_env_json,
                                     mock_read_deserialized_dev_env_org_json,
                                     mock_DevEnvOrgSetup, mock_DevEnvLocalSetup):
    # Test setup
    fake_local_images = [
        "axemsolutions/make_gnu_arm:v1.0.0",
        "axemsolutions/stlink_org:latest", 
        "axemsolutions/stlink_org:v1.0.0",
        "axemsolutions/cpputest:latest",
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/make_gnu_arm:v0.1.0", 
        "axemsolutions/make_gnu_arm:v1.1.0",
    ]
    fake_registry_images = [
        "axemsolutions/make_gnu_arm:latest", 
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest", 
        "axemsolutions/cmake:latest",
        "axemsolutions/llvm:latest",
        "axemsolutions/pemicro:latest",
        "axemsolutions/unity:latest",
        "axemsolutions/bazel:latest",
        "axemsolutions/gnu_arm:latest",
        "axemsolutions/jlink:latest",
    ]
    fake_dev_env_org_json_deserialized = json.loads(fake_data.dev_env_org_json)
    mock_read_deserialized_dev_env_org_json.return_value = fake_dev_env_org_json_deserialized
    fake_dev_env_org_setup = MagicMock()
    fake_org_dev_envs = []
    for dev_env_descriptor in fake_dev_env_org_json_deserialized["development_environments"]:
        fake_org_dev_envs.append(dev_env_setup.DevEnvOrg(descriptor=dev_env_descriptor))
    fake_dev_env_org_setup.dev_envs = fake_org_dev_envs
    mock_DevEnvOrgSetup.return_value = fake_dev_env_org_setup

    fake_container_engine = MagicMock()
    fake_container_engine.get_local_tool_images.return_value = fake_local_images
    mock_ContainerEngine.return_value = fake_container_engine
    mock_list_repos.return_value = fake_registry_images

    fake_dev_env_local_json_deserialized = json.loads(fake_data.dev_env_json)
    mock_read_deserialized_dev_env_json.return_value = fake_dev_env_local_json_deserialized
    fake_dev_env_local_setup = MagicMock()
    fake_local_dev_envs = []
    for dev_env_descriptor in fake_dev_env_local_json_deserialized["development_environments"]:
        fake_local_dev_envs.append(dev_env_setup.DevEnvLocal(descriptor=dev_env_descriptor))
    fake_dev_env_local_setup.dev_envs = fake_local_dev_envs
    mock_DevEnvLocalSetup.return_value = fake_dev_env_local_setup

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--env"])

    # Check expectations
    mock_read_deserialized_dev_env_org_json.assert_called_once()
    mock_DevEnvOrgSetup.assert_called_once_with(fake_dev_env_org_json_deserialized)
    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called_once()
    mock_list_repos.assert_called_once()

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

## Test listing the local tool images.

@patch("dem.cli.command.list_cmd.container_engine.ContainerEngine")
def test_local_tool_images(mock_ContainerEngine):
    # Test setup
    fake_local_tool_images = [
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest",
        "axemsolutions/make_gnu_arm:latest",
    ]
    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    fake_container_engine.get_local_tool_images.return_value = fake_local_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called_once()
    
    expected_table = Table()
    expected_table.add_column("Repository")
    expected_table.add_row("axemsolutions/cpputest:latest")
    expected_table.add_row("axemsolutions/stlink_org:latest")
    expected_table.add_row("axemsolutions/make_gnu_arm:latest")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.list_cmd.container_engine.ContainerEngine")
def test_no_local_tool_images(mock_ContainerEngine):
    # Test setup
    fake_local_tool_images = []
    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    fake_container_engine.get_local_tool_images.return_value = fake_local_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--local", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called_once()
    
    expected_table = Table()
    expected_table.add_column("Repository")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

## Test listing the local tool images.

@patch("dem.cli.command.list_cmd.registry.list_repos")
def test_registry_tool_images(mock_list_repos):
    # Test setup
    fake_registry_tool_images = [
        "axemsolutions/cpputest:latest",
        "axemsolutions/stlink_org:latest",
        "axemsolutions/make_gnu_arm:latest",
    ]
    mock_list_repos.return_value = fake_registry_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_list_repos.assert_called_once()
    
    expected_table = Table()
    expected_table.add_column("Repository")
    expected_table.add_row("axemsolutions/cpputest:latest")
    expected_table.add_row("axemsolutions/stlink_org:latest")
    expected_table.add_row("axemsolutions/make_gnu_arm:latest")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout

@patch("dem.cli.command.list_cmd.registry.list_repos")
def test_empty_repository(mock_list_repos):
    # Test setup
    fake_registry_tool_images = []
    mock_list_repos.return_value = fake_registry_tool_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["list", "--all", "--tool"])

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_list_repos.assert_called_once()
    
    expected_table = Table()
    expected_table.add_column("Repository")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    assert console.file.getvalue() == runner_result.stdout
