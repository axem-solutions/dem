# tests/test_dem.py

import io
import dem.cli.main as main
from typer.testing import CliRunner
from dem import __app_name__, __version__
from rich.console import Console
from rich.table import Table
import unittest
from unittest.mock import patch
import json

runner = CliRunner()

test_dev_env_json = """{
	"version": "0.1",
	"development_environments": [{
			"name": "demo",
			"tools": [{
					"type": "build_system",
					"tool_info": "gcc-arm-none-eabi 10.3-2021.10",
					"image_name": "make_gnu_arm",
					"image_version": "latest"
				},
				{
					"type": "toolchain",
					"tool_info": "gcc-arm-none-eabi 10.3-2021.10",
					"image_name": "make_gnu_arm",
					"image_version": "latest"
				},
				{
					"type": "debugger",
					"tool_info": "",
					"image_name": "stlink_org",
					"image_version": "latest"
				},
				{
					"type": "deployer",
					"tool_info": "",
					"image_name": "stlink_org",
					"image_version": "latest"
				},
				{
					"type": "test_framework",
					"tool_info": "",
					"image_name": "cpputest",
					"image_version": "latest"
				}
			]
		},
		{
			"name": "nagy_cica_project",
			"tools": [{
					"type": "build_system",
					"tool_info": "",
					"image_name": "bazel",
					"image_version": "latest"
				},
				{
					"type": "toolchain",
					"tool_info": "gcc-arm-none-eabi 10.3-2021.10",
					"image_name": "gnu_arm",
					"image_version": "latest"
				},
				{
					"type": "debugger",
					"tool_info": "",
					"image_name": "jlink",
					"image_version": "latest"
				},
				{
					"type": "deployer",
					"tool_info": "",
					"image_name": "jlink",
					"image_version": "latest"
				},
				{
					"type": "test_framework",
					"tool_info": "",
					"image_name": "cpputest",
					"image_version": "latest"
				}
			]
		}
	]
}
"""

test_empty_dev_env_json = """{
	"version": "0.1",
	"development_environments": []
}
"""
@patch("dem.cli.main.data_management.get_deserialized_dev_env_json")
def test_list_with_valid_dev_env_json(mock_get_deserialized_dev_env_json):
	expected_table = Table()
	expected_table.add_column("Development Environment")
	expected_table.add_column("Status")
	expected_table.add_row("demo", "[green]✓[/]")
	expected_table.add_row("nagy_cica_project", "[red]✗ Missing images[/]")
	console = Console(file=io.StringIO())
	console.print(expected_table)
	expected_output = console.file.getvalue()

	mock_get_deserialized_dev_env_json.return_value = json.loads(test_dev_env_json)

	result = runner.invoke(main.dem_typer_cli, "list")

	assert result.exit_code == 0
	assert result.stdout == expected_output 

@patch("dem.cli.main.data_management.get_deserialized_dev_env_json")
def test_list_with_empty_dev_env_json(mock_get_deserialized_dev_env_json):
	console = Console(file=io.StringIO())
	console.print("[yellow]No installed Development Environments.[/]")
	expected_output = console.file.getvalue()

	mock_get_deserialized_dev_env_json.return_value = json.loads(test_empty_dev_env_json)

	result = runner.invoke(main.dem_typer_cli, "list")

	assert result.exit_code == 0
	assert expected_output == result.stdout

def test_version():
	result = runner.invoke(main.dem_typer_cli, ["--version"])

	assert result.exit_code == 0
	assert f"{__app_name__} v{__version__}\n" in result.stdout