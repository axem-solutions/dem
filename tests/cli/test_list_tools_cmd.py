"""Unit tests for the list-tools CLI command."""
# tests/cli/test_list_tools_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.list_tools_cmd as list_tools_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call
from pytest import raises

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into 
# the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.list_tools_cmd.stdout.print")
def test_list_local_tools_no_local_tool_images(mock_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.tool_images.all_tool_images = {}
    
    # Run the test
    with raises(list_tools_cmd.typer.Abort):
        list_tools_cmd.list_local_tools(mock_platform)

    # Check the result
    mock_print.assert_called_once_with("[yellow]No local tool images are available.[/]")

@patch("dem.cli.command.list_tools_cmd.stdout.print")
def test_list_local_tools(mock_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_tool_image = MagicMock()
    mock_tool_image.name = "test_tool_image"
    mock_platform.tool_images.all_tool_images = {"test_tool_image": mock_tool_image}
    
    # Run the test
    list_tools_cmd.list_local_tools(mock_platform)

    # Check the result
    mock_print.assert_has_calls([call("\n [italic]Local Tool Images[/]"), 
                                 call("  test_tool_image")])

@patch("dem.cli.command.list_tools_cmd.stderr.print")
def test_update_tools_from_seleted_regs_unknown_registry(mock_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.config_file.registries = [{"name": "test_reg"}]
    
    # Run the test
    with raises(list_tools_cmd.typer.Abort):
        list_tools_cmd.update_tools_from_selected_regs(mock_platform, ["unknown_reg"])

    # Check the result
    mock_print.assert_called_once_with("[red]Error: Registry unknown_reg is not available![/]")

def test_update_tools_from_seleted_regs() -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.config_file.registries = [{"name": "test_reg"}]
    
    # Run the test
    list_tools_cmd.update_tools_from_selected_regs(mock_platform, ["test_reg"])

    # Check the result
    mock_platform.tool_images.update.assert_called_once_with(False, True, reg_selection={"test_reg"})

def test_list_tools_from_regs() -> None:
    # Setup
    mock_platform = MagicMock()
    mock_table = MagicMock()

    mock_tool_image1 = MagicMock()
    mock_tool_image1.name = "test_tool_image1"
    mock_tool_image1.availability = list_tools_cmd.ToolImage.REGISTRY_ONLY
    mock_tool_image2 = MagicMock()
    mock_tool_image2.name = "test_tool_image2"
    mock_tool_image2.availability = list_tools_cmd.ToolImage.LOCAL_AND_REGISTRY
    mock_tool_image3 = MagicMock()
    mock_tool_image3.name = "another_tool_image"
    mock_tool_image3.availability = list_tools_cmd.ToolImage.REGISTRY_ONLY

    mock_platform.tool_images.get_registry_ones.return_value = {
        "test_tool_image1": mock_tool_image1,
        "test_tool_image2": mock_tool_image2,
        "another_tool_image": mock_tool_image3
    }
    
    # Run the test
    list_tools_cmd.list_tools_from_regs(mock_platform, mock_table)

    # Check the result
    mock_table.add_column.assert_has_calls([call("Name"), call("Available locally?")])
    mock_platform.tool_images.get_registry_ones.assert_called_once()
    mock_table.add_row.assert_has_calls([call("another_tool_image", ""),
                                         call("test_tool_image1", ""),
                                         call("test_tool_image2", "[green]✔[/]")])

@patch("dem.cli.command.list_tools_cmd.stdout.print")
@patch("dem.cli.command.list_tools_cmd.list_tools_from_regs")
@patch("dem.cli.command.list_tools_cmd.Table")
@patch("dem.cli.command.list_tools_cmd.update_tools_from_selected_regs")
def test_list_tools_from_selected_regs(mock_update_tools_from_selected_regs: MagicMock,
                                       mock_Table: MagicMock,
                                       mock_list_tools_from_regs: MagicMock,
                                       mock_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_specified_regs = ["test_reg"]

    mock_table = MagicMock()
    mock_Table.return_value = mock_table

    mock_platform.tool_images.get_registry_ones.return_value = {
        "test_tool_image1": MagicMock(),
        "test_tool_image2": MagicMock()
    }

    # Run the test
    list_tools_cmd.list_tools_from_selected_regs(mock_platform, test_specified_regs)

    # Check the result
    mock_update_tools_from_selected_regs.assert_called_once_with(mock_platform, test_specified_regs)
    mock_platform.tool_images.get_registry_ones.assert_called_once()
    mock_Table.assert_called_once()
    mock_list_tools_from_regs.assert_called_once_with(mock_platform, mock_table)
    mock_print.assert_has_calls([call("\n [italic]Available Tool Images from the selected registries[/]"),
                                 call(mock_table)])

@patch("dem.cli.command.list_tools_cmd.stdout.print")
@patch("dem.cli.command.list_tools_cmd.update_tools_from_selected_regs")
def test_list_tools_from_selected_regs_no_available_tools(mock_update_tools_from_selected_regs: MagicMock,
                                                          mock_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_specified_regs = ["test_reg"]

    mock_platform.tool_images.get_registry_ones.return_value = {}

    # Run the test
    with raises(list_tools_cmd.typer.Abort):
        list_tools_cmd.list_tools_from_selected_regs(mock_platform, test_specified_regs)

    # Check the result
    mock_update_tools_from_selected_regs.assert_called_once_with(mock_platform, test_specified_regs)
    mock_platform.tool_images.get_registry_ones.assert_called_once()
    mock_print.assert_called_once_with("[yellow]No tool images are available in the selected registries.[/]")

@patch("dem.cli.command.list_tools_cmd.stdout.print")
@patch("dem.cli.command.list_tools_cmd.list_tools_from_regs")
@patch("dem.cli.command.list_tools_cmd.Table")
def test_list_tools_from_all_regs(mock_Table: MagicMock, mock_list_tools_from_regs: MagicMock,
                                  mock_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_table = MagicMock()

    mock_Table.return_value = mock_table
    mock_platform.tool_images.get_registry_ones.return_value = {
        "test_tool_image1": MagicMock(),
        "test_tool_image2": MagicMock()
    }

    # Run the test
    list_tools_cmd.list_tools_from_all_regs(mock_platform)

    # Check the result
    mock_platform.tool_images.update.assert_called_once_with(False, True)
    mock_platform.tool_images.get_registry_ones.assert_called_once()
    mock_Table.assert_called_once()
    mock_list_tools_from_regs.assert_called_once_with(mock_platform, mock_table)
    mock_print.assert_has_calls([call("\n [italic]Available Tool Images from all registries[/]"),
                                 call(mock_table)])

@patch("dem.cli.command.list_tools_cmd.stdout.print")
def test_list_tools_from_all_regs_no_available_tools(mock_print: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    mock_platform.tool_images.get_registry_ones.return_value = {}

    # Run the test
    with raises(list_tools_cmd.typer.Abort):
        list_tools_cmd.list_tools_from_all_regs(mock_platform)

    # Check the result
    mock_platform.tool_images.get_registry_ones.assert_called_once()
    mock_print.assert_called_once_with("[yellow]No tool images are available in the registries.[/]")

@patch("dem.cli.command.list_tools_cmd.list_local_tools")
def test_execute_list_local_tools(mock_list_local_tools: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()

    # Run the test
    list_tools_cmd.execute(mock_platform, False, [])

    # Check the result
    mock_list_local_tools.assert_called_once_with(mock_platform)

@patch("dem.cli.command.list_tools_cmd.list_tools_from_selected_regs")
def test_execute_list_tools_from_selected_regs(mock_list_tools_from_selected_regs: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    test_specified_regs = ["test_reg"]

    # Run the test
    list_tools_cmd.execute(mock_platform, True, test_specified_regs)

    # Check the result
    mock_list_tools_from_selected_regs.assert_called_once_with(mock_platform, test_specified_regs)

@patch("dem.cli.command.list_tools_cmd.list_tools_from_all_regs")
def test_execute_list_tools_from_all_regs(mock_list_tools_from_all_regs: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()

    # Run the test
    list_tools_cmd.execute(mock_platform, True, [])

    # Check the result
    mock_list_tools_from_all_regs.assert_called_once_with(mock_platform)

@patch("dem.cli.command.list_tools_cmd.execute")
def test_list_tools_cmd(mock_execute: MagicMock) -> None:
    # Setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    
    # Run the test
    result = runner.invoke(main.typer_cli, ["list-tools"])

    # Check the result
    assert result.exit_code == 0

    mock_execute.assert_called_once_with(mock_platform, False, [])