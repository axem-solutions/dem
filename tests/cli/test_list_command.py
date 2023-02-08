
# tests/test_dem.py

import io
import dem.cli.main as main
from typer.testing import CliRunner
from rich.console import Console
from rich.table import Table
from unittest.mock import patch
import json
import tests.cli.test_data as test_data

runner = CliRunner()

@patch("dem.cli.list_command.data_management.get_deserialized_dev_env_json")
def test_list_with_valid_dev_env_json(mock_get_deserialized_dev_env_json):
    expected_table = Table()
    expected_table.add_column("Development Environment")
    expected_table.add_column("Status")
    expected_table.add_row("demo", "[green]✓[/]")
    expected_table.add_row("nagy_cica_project", "[red]✗ Missing images[/]")
    console = Console(file=io.StringIO())
    console.print(expected_table)
    expected_output = console.file.getvalue()

    mock_get_deserialized_dev_env_json.return_value = json.loads(test_data.dev_env_json)

    result = runner.invoke(main.dem_typer_cli, "list")

    mock_get_deserialized_dev_env_json.assert_called_once()

    assert 0 == result.exit_code

    assert expected_output == result.stdout

@patch("dem.cli.list_command.data_management.get_deserialized_dev_env_json")
def test_list_with_empty_dev_env_json(mock_get_deserialized_dev_env_json):
    console = Console(file=io.StringIO())
    console.print("[yellow]No installed Development Environments.[/]")
    expected_output = console.file.getvalue()

    mock_get_deserialized_dev_env_json.return_value = json.loads(test_data.empty_dev_env_json)

    result = runner.invoke(main.dem_typer_cli, "list")

    mock_get_deserialized_dev_env_json.assert_called_once()

    assert 0 == result.exit_code

    assert expected_output == result.stdout