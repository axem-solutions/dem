"""Unit tests for the list CLI command."""
# tests/cli/test_list_command.py

import io
import dem.cli.main as main
from typer.testing import CliRunner
from rich.console import Console
from rich.table import Table
from unittest.mock import patch
import json
import tests.test_data as test_data

runner = CliRunner()

@patch("dem.cli.list_command.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.list_command.image_management.get_local_image_tags")
def test_list_with_valid_dev_env_json(mock_get_local_image_tags,
                                        mock_get_deserialized_dev_env_json):
    test_image_tags = [
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
    mock_get_deserialized_dev_env_json.return_value = json.loads(test_data.dev_env_json)
    mock_get_local_image_tags.return_value = test_image_tags

    result = runner.invoke(main.dem_typer_cli, "list")

    mock_get_deserialized_dev_env_json.assert_called_once()
    mock_get_local_image_tags.assert_called_once()

    assert 0 == result.exit_code

    expected_table = Table()
    expected_table.add_column("Development Environment")
    expected_table.add_column("Status")
    expected_table.add_row("demo", "[green]✓[/]")
    expected_table.add_row("nagy_cica_project", "[red]✗ Missing images[/]")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()
    assert expected_output == result.stdout

@patch("dem.cli.list_command.data_management.get_deserialized_dev_env_json")
@patch("dem.cli.list_command.image_management.get_local_image_tags")
def test_list_with_empty_dev_env_json(mock_get_local_image_tags,
                                        mock_get_deserialized_dev_env_json):
    test_image_tags = [
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

    mock_get_deserialized_dev_env_json.return_value = json.loads(test_data.empty_dev_env_json)
    mock_get_local_image_tags.return_value = test_image_tags

    result = runner.invoke(main.dem_typer_cli, "list")

    mock_get_deserialized_dev_env_json.assert_called_once()

    assert 0 == result.exit_code

    console = Console(file=io.StringIO())
    console.print("[yellow]No installed Development Environments.[/]")
    expected_output = console.file.getvalue()
    assert expected_output == result.stdout