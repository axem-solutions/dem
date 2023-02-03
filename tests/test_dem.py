# tests/test_dem.py

import io
import dem.cli.main as main
from typer.testing import CliRunner
from dem import __app_name__, __version__
from rich.console import Console
from rich.table import Table
import unittest
from unittest.mock import patch

runner = CliRunner()

def test_list():
	result = runner.invoke(main.dem_typer_cli, "list")

	expected_table = Table()
	expected_table.add_column("Development Environment")
	expected_table.add_column("Status")
	expected_table.add_row("demo", "[green]✓[/]")
	expected_table.add_row("nagy_cica_project", "[red]✗ Missing images[/]")
	console = Console(file=io.StringIO(), width=120)
	console.print(expected_table)
	expected_output = console.file.getvalue()

	assert result.exit_code == 0
	assert expected_output == result.stdout

def test_version():
	result = runner.invoke(main.dem_typer_cli, ["--version"])

	assert result.exit_code == 0
	assert f"{__app_name__} v{__version__}\n" in result.stdout