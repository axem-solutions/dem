"""Unit tests for the list CLI command."""
# tests/cli/test_list_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.list_cmd as list_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

def test_add_dev_env_info_to_table_installed_default() -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.default_dev_env_name = "test_dev_env"
    mock_tool_image = MagicMock()
    mock_platform.tool_images = mock_tool_image
    mock_table = MagicMock()
    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = True
    mock_dev_env.name = "test_dev_env"
    mock_dev_env.is_installation_correct.return_value = True

    # Run the test
    list_cmd.add_dev_env_info_to_table(mock_platform, mock_table, mock_dev_env)

    # Check the result
    mock_dev_env.assign_tool_image_instances.assert_called_once_with(mock_platform.tool_images)
    mock_dev_env.is_installation_correct.assert_called_once()
    mock_table.add_row.assert_called_once_with("test_dev_env", "[green]✓[/]", "[green]✓[/]", 
                                               "[green]Ok[/]")

def test_add_dev_env_info_to_table_installed_unavailable_image() -> None:
    # Setup
    mock_platform = MagicMock()
    mock_tool_image = MagicMock()
    mock_platform.tool_images = mock_tool_image
    mock_table = MagicMock()
    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = True
    mock_dev_env.name = "test_dev_env"
    mock_dev_env.is_installation_correct.return_value = False

    # Run the test
    list_cmd.add_dev_env_info_to_table(mock_platform, mock_table, mock_dev_env)

    # Check the result
    mock_dev_env.assign_tool_image_instances.assert_called_once_with(mock_platform.tool_images)
    mock_dev_env.is_installation_correct.assert_called_once()
    mock_table.add_row.assert_called_once_with("test_dev_env", "[green]✓[/]", "", "[red]Error: Incorrect installation![/]")

def test_add_dev_env_info_to_table_not_installed() -> None:
    # Setup
    mock_platform = MagicMock()
    mock_tool_image = MagicMock()
    mock_platform.tool_images = mock_tool_image
    mock_table = MagicMock()
    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = False
    mock_dev_env.name = "test_dev_env"

    # Run the test
    list_cmd.add_dev_env_info_to_table(mock_platform, mock_table, mock_dev_env)

    # Check the result
    mock_dev_env.assign_tool_image_instances.assert_not_called()
    mock_dev_env.get_tool_image_status.assert_not_called()
    mock_table.add_row.assert_called_once_with("test_dev_env", "", "", "[green]Ok[/]")

@patch("dem.cli.command.list_cmd.stdout.print")
def test_list_local_dev_envs_no_dev_envs(mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.local_dev_envs = []

    # Run the test
    list_cmd.list_local_dev_envs(mock_platform)

    # Check the result
    mock_stdout_print.assert_called_once_with("[yellow]No Development Environment descriptors are available.[/]")

@patch("dem.cli.command.list_cmd.stdout.print")
@patch("dem.cli.command.list_cmd.Table")
@patch("dem.cli.command.list_cmd.add_dev_env_info_to_table")
def test_list_local_dev_envs(mock_add_dev_env_info_to_table: MagicMock, mock_Table: MagicMock,
                             mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_table = MagicMock()
    mock_Table.return_value = mock_table
    mock_dev_env = MagicMock()
    mock_dev_env.name = "test_dev_env"
    mock_platform.local_dev_envs = [mock_dev_env]

    # Run the test
    list_cmd.list_local_dev_envs(mock_platform)

    # Check the result
    mock_table.add_column.assert_has_calls([call("Name"), 
                                            call("Installed", justify="center"), 
                                            call("Default", justify="center"), 
                                            call("Status", justify="center")])
    mock_add_dev_env_info_to_table.assert_called_once_with(mock_platform, mock_table, mock_dev_env)
    mock_stdout_print.assert_has_calls([call(f"\n [italic]Local Development Environments[/]"), 
                                        call(mock_table)])

@patch("dem.cli.command.list_cmd.stdout.print")
def test_list_actual_cat_dev_envs_no_dev_envs(mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_catalog = MagicMock()
    mock_catalog.name = "test_catalog"
    mock_catalog.dev_envs = []

    # Run the test
    list_cmd.list_actual_cat_dev_envs(mock_catalog)

    # Check the result
    mock_catalog.request_dev_envs.assert_called_once()
    mock_stdout_print.assert_called_once_with("[yellow]No Development Environments are available in the test_catalog catalog.[/]")

@patch("dem.cli.command.list_cmd.stdout.print")
@patch("dem.cli.command.list_cmd.Table")
def test_list_actual_cat_dev_envs(mock_Table: MagicMock, mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_catalog = MagicMock()
    mock_catalog.name = "test_catalog"
    mock_dev_env = MagicMock()
    mock_dev_env.name = "test_dev_env"
    mock_catalog.dev_envs = [mock_dev_env]
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    # Run the test
    list_cmd.list_actual_cat_dev_envs(mock_catalog)

    # Check the result
    mock_catalog.request_dev_envs.assert_called_once()
    mock_table.add_column.assert_called_once_with("Name")
    mock_table.add_row.assert_called_once_with("test_dev_env")
    mock_stdout_print.assert_has_calls([call(f"\n [italic]Development Environments in the test_catalog catalog:[/]"), 
                                        call(mock_table)])
                                        
@patch("dem.cli.command.list_cmd.stdout.print")
def test_list_all_cat_dev_envs_no_catalogs(mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.dev_env_catalogs.catalogs = []

    # Run the test
    list_cmd.list_all_cat_dev_envs(mock_platform)

    # Check the result
    mock_stdout_print.assert_called_once_with("[yellow]No Development Environment Catalogs are available!")

@patch("dem.cli.command.list_cmd.list_actual_cat_dev_envs")
def test_list_all_cat_dev_envs(mock_list_actual_cat_dev_envs: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_catalog = MagicMock()
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run the test
    list_cmd.list_all_cat_dev_envs(mock_platform)

    # Check the result
    mock_list_actual_cat_dev_envs.assert_called_once_with(mock_catalog)

@patch("dem.cli.command.list_cmd.list_actual_cat_dev_envs")
def test_list_selected_cat_dev_envs(mock_list_actual_cat_dev_envs: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_catalog = MagicMock()
    test_catalog_name = "test_catalog"
    mock_catalog.name = test_catalog_name
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run the test
    list_cmd.list_selected_cat_dev_envs(mock_platform, [test_catalog_name])

    # Check the result
    mock_list_actual_cat_dev_envs.assert_called_once_with(mock_catalog)

@patch("dem.cli.command.list_cmd.stderr.print")
def test_list_selected_cat_dev_envs_catalog_not_found(mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_catalog = MagicMock()
    test_catalog_name = "test_catalog"
    mock_catalog.name = test_catalog_name
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run the test
    list_cmd.list_selected_cat_dev_envs(mock_platform, ["wrong_catalog"])

    # Check the result
    mock_stderr_print.assert_called_once_with("[red]Error: Catalog 'wrong_catalog' not found![/]")

@patch("dem.cli.command.list_cmd.list_all_cat_dev_envs")
def test_execute_list_all_cat_dev_envs(mock_list_all_cat_dev_envs: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()

    # Run the test
    list_cmd.execute(mock_platform, True, [])

    # Check the result
    mock_list_all_cat_dev_envs.assert_called_once_with(mock_platform)

@patch("dem.cli.command.list_cmd.list_selected_cat_dev_envs")
def test_execute_list_selected_cat_dev_envs(mock_list_selected_cat_dev_envs: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()

    # Run the test
    list_cmd.execute(mock_platform, True, ["test_catalog"])

    # Check the result
    mock_list_selected_cat_dev_envs.assert_called_once_with(mock_platform, ["test_catalog"])

@patch("dem.cli.command.list_cmd.stdout.print")
@patch("dem.cli.command.list_cmd.list_local_dev_envs")
def test_execute_list_local_dev_envs(mock_list_local_dev_envs: MagicMock, 
                                     mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.default_dev_env_name = "test_dev_env"

    # Run the test
    list_cmd.execute(mock_platform, False, [])

    # Check the result
    mock_list_local_dev_envs.assert_called_once_with(mock_platform)
    mock_stdout_print.assert_called_once_with(f"\n[bold]The default Development Environment: test_dev_env[/]")

@patch("dem.cli.command.list_cmd.execute")
def test_main_list(mock_execute: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    # Run the test
    result = runner.invoke(main.typer_cli, ["list", "--cat", "test_catalog"])

    # Check the result
    assert result.exit_code == 0

    mock_execute.assert_called_once_with(mock_platform, True, ["test_catalog"])