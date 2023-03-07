"""Unit tests for the info CLI command."""
# tests/cli/test_info_command.py

from typer.testing import CliRunner
import dem.cli.main as main
from unittest.mock import patch, MagicMock
import docker 
from rich.console import Console
from rich.table import Table
import io
import tests.fake_data as fake_data
import json

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

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

test_docker_client = docker.from_env()

@patch("dem.cli.command.info_command.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.command.info_command.container_engine.ContainerEngine")
@patch("dem.cli.command.info_command.registry.list_repos")
def test_info_arg_demo(mock_list_repos, mock_ContainerEngine, mock_get_deserialized_dev_env_json):
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
    #Mocks
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_image_tags.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images

    runner_result = runner.invoke(main.typer_cli, ["info", "demo"], color=True)
    mock_get_deserialized_dev_env_json.assert_called_once()
    mock_list_repos.assert_called_once()

    expected_table = Table()
    expected_table.add_column("Type")
    expected_table.add_column("Image")
    expected_table.add_column("Status")
    expected_table.add_row("build system", "make_gnu_arm:latest", "Image is available locally and in the registry.")
    expected_table.add_row("toolchain", "make_gnu_arm:latest", "Image is available locally and in the registry.")
    expected_table.add_row("debugger", "stlink_org:latest", "Image is available locally and in the registry.")
    expected_table.add_row("deployer", "stlink_org:latest", "Image is available locally and in the registry.")
    expected_table.add_row("test framework", "cpputest:latest", "Image is available locally and in the registry.")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()

    assert 0 == runner_result.exit_code

    assert expected_output == runner_result.stdout


@patch("dem.cli.command.info_command.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.command.info_command.container_engine.ContainerEngine")
@patch("dem.cli.command.info_command.registry.list_repos")
def test_info_arg_nagy_cica_project(mock_list_repos, mock_ContainerEngine, 
                                    mock_get_deserialized_dev_env_json):
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
    #Mocks
    mock_get_deserialized_dev_env_json.return_value = json.loads(fake_data.dev_env_json)
    mock_container_engine = MagicMock()
    mock_container_engine.get_local_image_tags.return_value = test_local_images
    mock_ContainerEngine.return_value = mock_container_engine
    mock_list_repos.return_value = test_registry_images

    runner_result = runner.invoke(main.typer_cli, ["info", "nagy_cica_project"], color=True)

    mock_get_deserialized_dev_env_json.assert_called_once()
    mock_list_repos.assert_called_once()

    expected_table = Table()
    expected_table.add_column("Type")
    expected_table.add_column("Image")
    expected_table.add_column("Status")
    expected_table.add_row("build system", "bazel:latest", "[red]Error: Image is not available.[/]")
    expected_table.add_row("toolchain", "gnu_arm:latest", "[red]Error: Image is not available.[/]")
    expected_table.add_row("debugger", "jlink:latest", "[red]Error: Image is not available.[/]")
    expected_table.add_row("deployer", "jlink:latest", "[red]Error: Image is not available.[/]")
    expected_table.add_row("test framework", "cpputest:latest", "Image is available locally and in the registry.")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()

    assert 0 == runner_result.exit_code

    assert expected_output == runner_result.stdout

def test_info_arg_invalid():
    runner_result = runner.invoke(main.typer_cli, ["info", "not_existing_environment"])

    assert 0 == runner_result.exit_code

    console = Console(file=io.StringIO())
    console.print("[red]Error: Unknown Development Environment: not_existing_environment[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stderr