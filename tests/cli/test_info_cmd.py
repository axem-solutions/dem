"""Unit tests for the info CLI command."""
# tests/cli/test_info_cmd.py

from typer.testing import CliRunner
import dem.cli.main as main
from unittest.mock import patch, MagicMock
import docker 
from rich.console import Console
from rich.table import Table
import io
import tests.fake_data as fake_data
import json

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)
test_docker_client = docker.from_env()

## Test helpers

class mockImage:
    def __init__(self, tags: list[str]):
        self.tags = tags

def get_test_image_list() -> list[mockImage]:
    test_image_list = []
    test_image_list.append(mockImage(["alpine:latest"]))
    test_image_list.append(mockImage([""]))
    test_image_list.append(mockImage(["make_gnu_arm:v1.0.0"]))
    test_image_list.append(mockImage(["stlink_org:latest", "stlink_org:v1.0.0'"]))
    test_image_list.append(mockImage(["cpputest:latest"]))
    test_image_list.append(mockImage(["make_gnu_arm:latest"]))
    test_image_list.append(mockImage(["debian:latest"]))
    test_image_list.append(mockImage(["ubuntu:latest"]))
    test_image_list.append(mockImage(["hello-world:latest"]))
    test_image_list.append(mockImage([""]))
    return test_image_list

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

@patch("dem.cli.command.info_cmd.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.command.info_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.info_cmd.registry.list_repos")
def test_info_arg_demo(mock_list_repos, mock_ContainerEngine, mock_get_deserialized_dev_env_json):
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
    runner_result = runner.invoke(main.typer_cli, ["info", "demo"], color=True)

    # Check expectations
    mock_get_deserialized_dev_env_json.assert_called_once()
    mock_list_repos.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_tools = [
        ["build system", "make_gnu_arm:latest", "Image is available locally and in the registry."],
        ["toolchain", "make_gnu_arm:latest", "Image is available locally and in the registry."],
        ["debugger", "stlink_org:latest", "Image is available locally and in the registry."],
        ["deployer", "stlink_org:latest", "Image is available locally and in the registry."],
        ["test framework", "cpputest:latest", "Image is available locally and in the registry."],
    ]
    assert get_expected_table(expected_tools)  == runner_result.stdout


@patch("dem.cli.command.info_cmd.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.command.info_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.info_cmd.registry.list_repos")
def test_info_arg_nagy_cica_project(mock_list_repos, mock_ContainerEngine, 
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
        "jlink:latest",
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
    runner_result = runner.invoke(main.typer_cli, ["info", "nagy_cica_project"], color=True)

    # Check expectations
    mock_get_deserialized_dev_env_json.assert_called_once()
    mock_list_repos.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_tools = [
        ["build system", "bazel:latest", "[red]Error: Image is not available.[/]"],
        ["toolchain", "gnu_arm:latest", "[red]Error: Image is not available.[/]"],
        ["debugger", "jlink:latest", "Image is available locally."],
        ["deployer", "jlink:latest", "Image is available locally."],
        ["test framework", "cpputest:latest", "Image is available locally and in the registry."],
    ]
    assert get_expected_table(expected_tools) == runner_result.stdout

def test_info_arg_invalid():
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["info", "not_existing_environment"])

    # Check expectations
    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: Unknown Development Environment: not_existing_environment[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stderr

@patch("dem.cli.command.info_cmd.data_management.get_deserialized_dev_env_org_json")
@patch("dem.cli.command.info_cmd.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.command.info_cmd.container_engine.ContainerEngine")
@patch("dem.cli.command.info_cmd.registry.list_repos")
def test_info_org_dev_env(mock_list_repos, mock_ContainerEngine, 
                                    mock_get_deserialized_dev_env_json,
                                    mock_get_deserialized_dev_env_org_json):
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
        "unity:latest"
    ]
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_get_deserialized_dev_env_org_json.return_value = json.loads(fake_data.dev_env_org_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_image_tags.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["info", "org_only_env"])

    # Check expectations
    mock_get_deserialized_dev_env_json.assert_called_once()
    mock_get_deserialized_dev_env_org_json.assert_called_once()
    mock_container_engine.get_local_image_tags.assert_called_once()
    mock_list_repos.assert_called_once()

    assert 0 == runner_result.exit_code

    expected_tools = [
        ["build system", "cmake:latest", "Image is available in the registry."],
        ["toolchain", "llvm:latest", "Image is available in the registry."],
        ["debugger", "pemicro:latest", "Image is available in the registry."],
        ["deployer", "pemicro:latest", "Image is available in the registry."],
        ["test framework", "unity:latest", "Image is available in the registry."],
    ]
    assert get_expected_table(expected_tools) == runner_result.stdout