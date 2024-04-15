"""Unit tests for the info CLI command."""
# tests/cli/test_info_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.info_cmd as info_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import MagicMock, call, patch
from pytest import raises

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.info_cmd.stdout.print")
@patch("dem.cli.command.info_cmd.Table")
def test_print_local_dev_env_info_installed(mock_Table: MagicMock, 
                                            mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_dev_env = MagicMock()
    mock_dev_env.name = "test_dev_env"
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "tool_image1"
    mock_tool_image1.availability = info_cmd.ToolImage.LOCAL_ONLY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "tool_image2"
    mock_tool_image2.availability = info_cmd.ToolImage.LOCAL_AND_REGISTRY
    mock_dev_env.tool_images = [mock_tool_image1, mock_tool_image2]
    mock_dev_env.is_installed = True

    # Run the test
    info_cmd.print_local_dev_env_info(mock_dev_env)

    # Verify the output
    mock_Table.assert_called_once()
    mock_table.add_column.assert_has_calls([call("Image"), call("Availability")])
    mock_table.add_row.assert_has_calls([call("tool_image1", "Local"),
                                        call("tool_image2", "Local and Registry")])
    mock_stdout_print.assert_has_calls([call("\n[bold]Development Environment: test_dev_env[/]\n"),
                                        call("Installation state: [green]Installed[/]\n"),
                                        call(mock_table)])

@patch("dem.cli.command.info_cmd.stdout.print")
@patch("dem.cli.command.info_cmd.Table")
def test_print_local_dev_env_info_not_installed(mock_Table: MagicMock, 
                                                mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_dev_env = MagicMock()
    mock_dev_env.name = "test_dev_env"
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "tool_image1"
    mock_tool_image1.availability = info_cmd.ToolImage.LOCAL_ONLY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "tool_image2"
    mock_tool_image2.availability = info_cmd.ToolImage.LOCAL_AND_REGISTRY
    mock_dev_env.tool_images = [mock_tool_image1, mock_tool_image2]
    mock_dev_env.is_installed = False

    # Run the test
    info_cmd.print_local_dev_env_info(mock_dev_env)

    # Verify the output
    mock_Table.assert_called_once()
    mock_table.add_column.assert_has_calls([call("Image"), call("Availability")])
    mock_table.add_row.assert_has_calls([call("tool_image1", "Local"),
                                        call("tool_image2", "Local and Registry")])
    mock_stdout_print.assert_has_calls([call("\n[bold]Development Environment: test_dev_env[/]\n"),
                                        call("Installation state: Not installed\n"),
                                        call(mock_table)])

@patch("dem.cli.command.info_cmd.stdout.print")
@patch("dem.cli.command.info_cmd.stderr.print")
@patch("dem.cli.command.info_cmd.Table")
def test_print_local_dev_env_info_reinstall_needed(mock_Table: MagicMock, 
                                                  mock_stderr_print: MagicMock,
                                                  mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_dev_env = MagicMock()
    mock_dev_env.name = "test_dev_env"
    mock_table = MagicMock()
    mock_Table.return_value = mock_table
    
    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "tool_image1"
    mock_tool_image1.availability = info_cmd.ToolImage.LOCAL_ONLY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "tool_image2"
    mock_tool_image2.availability = info_cmd.ToolImage.LOCAL_AND_REGISTRY
    mock_dev_env.tool_images = [mock_tool_image1, mock_tool_image2]
    mock_dev_env.is_installed = True
    mock_dev_env.get_tool_image_status.return_value = info_cmd.DevEnv.Status.REINSTALL_NEEDED

    # Run the test
    info_cmd.print_local_dev_env_info(mock_dev_env)

    # Verify the output
    mock_Table.assert_called_once()
    mock_table.add_column.assert_has_calls([call("Image"), call("Availability")])
    mock_table.add_row.assert_has_calls([call("tool_image1", "Local"),
                                        call("tool_image2", "Local and Registry")])
    mock_stdout_print.assert_has_calls([call("\n[bold]Development Environment: test_dev_env[/]\n"),
                                        call("Installation state: [green]Installed[/]\n"),
                                        call(mock_table)])
    mock_stderr_print.assert_called_once_with("\n[red]Error: Incomplete local install! The Dev Env must be reinstalled![/]")

@patch("dem.cli.command.info_cmd.stdout.print")
@patch("dem.cli.command.info_cmd.stderr.print")
@patch("dem.cli.command.info_cmd.Table")
def test_print_local_dev_env_info_unavailable_image(mock_Table: MagicMock, 
                                                    mock_stderr_print: MagicMock,
                                                    mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_dev_env = MagicMock()
    mock_dev_env.name = "test_dev_env"
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "tool_image1"
    mock_tool_image1.availability = info_cmd.ToolImage.LOCAL_ONLY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "tool_image2"
    mock_tool_image2.availability = info_cmd.ToolImage.LOCAL_AND_REGISTRY
    mock_dev_env.tool_images = [mock_tool_image1, mock_tool_image2]
    mock_dev_env.is_installed = False
    mock_dev_env.get_tool_image_status.return_value = info_cmd.DevEnv.Status.UNAVAILABLE_IMAGE

    # Run the test
    info_cmd.print_local_dev_env_info(mock_dev_env)

    # Verify the output
    mock_Table.assert_called_once()
    mock_table.add_column.assert_has_calls([call("Image"), call("Availability")])
    mock_table.add_row.assert_has_calls([call("tool_image1", "Local"),
                                        call("tool_image2", "Local and Registry")])
    mock_stdout_print.assert_has_calls([call("\n[bold]Development Environment: test_dev_env[/]\n"),
                                        call("Installation state: Not installed\n"),
                                        call(mock_table)])
    mock_stderr_print.assert_called_once_with("\n[red]Error: Required image could not be found either locally or in the registry![/]")

@patch("dem.cli.command.info_cmd.print_local_dev_env_info")
def test_local_info(mock_print_local_dev_env_info: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_dev_env = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run the test
    info_cmd.local_info(mock_platform, "test_dev_env")

    # Verify the output
    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with("test_dev_env")
    mock_print_local_dev_env_info.assert_called_once_with(mock_dev_env)

@patch("dem.cli.command.info_cmd.stderr.print")
def test_local_info_unknown_dev_env(mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None

    # Run the test
    with raises(info_cmd.typer.Abort):
        info_cmd.local_info(mock_platform, "unknown_dev_env")

    # Verify the output
    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with("unknown_dev_env")
    mock_stderr_print.assert_called_once_with("[red]Error: Unknown Development Environment: unknown_dev_env[/]\n")

@patch("dem.cli.command.info_cmd.stdout.print")
@patch("dem.cli.command.info_cmd.Table")
def test_print_cat_dev_env_info(mock_Table: MagicMock, 
                                mock_stdout_print: MagicMock) -> None:
    # Setup
    mock_dev_env = MagicMock()
    mock_dev_env.name = "test_dev_env"
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "tool_image1"
    mock_tool_image1.availability = info_cmd.ToolImage.REGISTRY_ONLY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "tool_image2"
    mock_tool_image2.availability = info_cmd.ToolImage.LOCAL_AND_REGISTRY
    mock_dev_env.tool_images = [mock_tool_image1, mock_tool_image2]
    mock_dev_env.get_tool_image_status.return_value = info_cmd.DevEnv.Status.OK

    # Run the test
    info_cmd.print_cat_dev_env_info(mock_dev_env, "test_cat")

    # Verify the output
    mock_Table.assert_called_once()
    mock_table.add_column.assert_has_calls([call("Image"), call("Availability")])
    mock_table.add_row.assert_has_calls([call("tool_image1", "Registry"),
                                        call("tool_image2", "Local and Registry")])
    mock_stdout_print.assert_has_calls([call("\n[bold]Development Environment: test_dev_env[/]\n"),
                                        call(f"Catalog: test_cat\n"),
                                        call(mock_table)])

@patch("dem.cli.command.info_cmd.stderr.print")
@patch("dem.cli.command.info_cmd.stdout.print")
@patch("dem.cli.command.info_cmd.Table")
def test_print_cat_dev_env_info_unavailable_image(mock_Table: MagicMock, 
                                                  mock_stdout_print: MagicMock,
                                                  mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_dev_env = MagicMock()
    mock_dev_env.name = "test_dev_env"
    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "tool_image1"
    mock_tool_image1.availability = info_cmd.ToolImage.REGISTRY_ONLY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "tool_image2"
    mock_tool_image2.availability = info_cmd.ToolImage.LOCAL_AND_REGISTRY
    mock_dev_env.tool_images = [mock_tool_image1, mock_tool_image2]
    mock_dev_env.get_tool_image_status.return_value = info_cmd.DevEnv.Status.UNAVAILABLE_IMAGE

    # Run the test
    info_cmd.print_cat_dev_env_info(mock_dev_env, "test_cat")

    # Verify the output
    mock_Table.assert_called_once()
    mock_table.add_column.assert_has_calls([call("Image"), call("Availability")])
    mock_table.add_row.assert_has_calls([call("tool_image1", "Registry"),
                                        call("tool_image2", "Local and Registry")])
    mock_stdout_print.assert_has_calls([call("\n[bold]Development Environment: test_dev_env[/]\n"),
                                        call(f"Catalog: test_cat\n"),
                                        call(mock_table)])
    mock_stderr_print.assert_called_once_with("\n[red]Error: Required image could not be found in the registry![/]")

@patch("dem.cli.command.info_cmd.print_cat_dev_env_info")
def test_cat_dev_env_info(mock_print_cat_dev_env_info: MagicMock) -> None:
    # Setup
    mock_dev_env = MagicMock()
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env"
    mock_catalog = MagicMock()
    mock_catalog.get_dev_env_by_name.return_value = mock_dev_env
    mock_catalog.name = "test_cat"
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run the test
    info_cmd.cat_dev_env_info(mock_platform, test_dev_env_name, [])

    # Verify the output
    mock_catalog.request_dev_envs.assert_called_once()
    mock_catalog.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_print_cat_dev_env_info.assert_called_once_with(mock_dev_env, "test_cat")

@patch("dem.cli.command.info_cmd.stderr.print")
def test_cat_dev_env_info_unknown_dev_env(mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env"
    mock_catalog = MagicMock()
    mock_catalog.get_dev_env_by_name.return_value = None
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run the test
    info_cmd.cat_dev_env_info(mock_platform, test_dev_env_name, [])

    # Verify the output
    mock_catalog.request_dev_envs.assert_called_once()
    mock_catalog.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stderr_print.assert_called_once_with("[red]Error: Unknown Development Environment: test_dev_env[/]\n")

@patch("dem.cli.command.info_cmd.stderr.print")
def test_selected_cats_info_unknown_catalog(mock_stderr_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env"
    mock_catalog = MagicMock()
    mock_catalog.name = "test_cat"
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run the test
    with raises(info_cmd.typer.Abort):
        info_cmd.selected_cats_info(mock_platform, test_dev_env_name, ["unknown_cat"])

    # Verify the output
    mock_stderr_print.assert_called_once_with("[red]Error: Unknown catalog(s): unknown_cat[/]\n")

@patch("dem.cli.command.info_cmd.cat_dev_env_info")
def test_selected_cats_info(mock_cat_dev_env_info: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env"
    mock_catalog = MagicMock()
    mock_catalog.name = "test_cat"
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]

    # Run the test
    info_cmd.selected_cats_info(mock_platform, test_dev_env_name, ["test_cat"])

    # Verify the output
    mock_cat_dev_env_info.assert_called_once_with(mock_platform, test_dev_env_name, { "test_cat" })

@patch("dem.cli.command.info_cmd.cat_dev_env_info")
def test_all_cats_info(mock_cat_dev_env_info: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env"

    # Run the test
    info_cmd.all_cats_info(mock_platform, test_dev_env_name)

    # Verify the output
    mock_cat_dev_env_info.assert_called_once_with(mock_platform, test_dev_env_name, [])

@patch("dem.cli.command.info_cmd.local_info")
def test_execute_local_info(mock_local_info: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env"

    # Run the test
    info_cmd.execute(mock_platform, test_dev_env_name, False, [])

    # Verify the output
    mock_local_info.assert_called_once_with(mock_platform, test_dev_env_name)

@patch("dem.cli.command.info_cmd.selected_cats_info")
def test_execute_selected_cats_info(mock_selected_cats_info: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env"

    # Run the test
    info_cmd.execute(mock_platform, test_dev_env_name, True, ["test_cat"])

    # Verify the output
    mock_selected_cats_info.assert_called_once_with(mock_platform, test_dev_env_name, ["test_cat"])

@patch("dem.cli.command.info_cmd.all_cats_info")
def test_execute_all_cats_info(mock_all_cats_info: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env"

    # Run the test
    info_cmd.execute(mock_platform, test_dev_env_name, True, [])

    # Verify the output
    mock_all_cats_info.assert_called_once_with(mock_platform, test_dev_env_name)

@patch("dem.cli.command.info_cmd.execute")
def test_info_cmd(mock_execute: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    # Run the test
    result = runner.invoke(main.typer_cli, ["info", "test_dev_env"])

    # Verify the output
    assert result.exit_code == 0

    mock_execute.assert_called_once_with(mock_platform, "test_dev_env", False, [])