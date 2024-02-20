"""Tests for the modify command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.modify_cmd as modify_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from rich.console import Console
import io, typer

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

def test_get_tool_image_list():
    # Test setup
    mock_tool_images = MagicMock()
    mock_tool_images.registry.elements = [
        "local_and_registry_image",
        "registry_image",
    ]
    mock_tool_images.local.elements = [
        "local_image",
        "local_and_registry_image",
    ]

    # Run unit under test
    actual_tool_images = modify_cmd.get_tool_image_list(mock_tool_images)

    # Check expectations
    expected_tool_iamges = [
        ["local_and_registry_image", "local and registry"],
        ["registry_image", "registry"],
        ["local_image", "local"],
    ]
    assert actual_tool_images == expected_tool_iamges

@patch("dem.cli.command.modify_cmd.SelectMenu")
def test_get_confirm_from_user(mock_SelectMenu):
    # Test setup
    mock_select_menu = MagicMock()
    mock_SelectMenu.return_value = mock_select_menu
    expected_selected_item = "confirm"
    mock_select_menu.get_selected.return_value = expected_selected_item

    # Run unit under test
    actual_selected_item = modify_cmd.get_confirm_from_user()

    # Check expectations
    expected_menu_items = ["confirm", "save as", "cancel"]
    mock_SelectMenu.assert_called_once_with(expected_menu_items)
    mock_select_menu.set_title.assert_called_once_with("Are you sure to overwrite the Development Environment?")
    mock_select_menu.wait_for_user.assert_called_once()

    assert actual_selected_item == expected_selected_item

def test_handle_user_confirm_confirmed():
    # Test setup
    mock_deserialized_local_dev_env = MagicMock()
    mock_platform = MagicMock()
    mock_platform.get_deserialized.return_value = mock_deserialized_local_dev_env

    # Run unit under test
    modify_cmd.handle_user_confirm("confirm", MagicMock(), mock_platform)

    # Check expectation
    mock_platform.flush_descriptors.assert_called_once()

@patch("dem.cli.command.modify_cmd.typer.prompt")
def test_handle_user_confirm_save_as(mock_prompt):
    # Test setup    
    mock_prompt.return_value = "test new name"
    mock_deserialized_local_dev_env = MagicMock()
    mock_platform = MagicMock()
    mock_platform.get_deserialized.return_value = mock_deserialized_local_dev_env
    mock_platform.get_dev_env_by_name.return_value = None
    mock_dev_env_local = MagicMock()
    mock_dev_env_local.name = "fake dev env"
    mock_platform.local_dev_envs = [mock_dev_env_local]
    
    # Run unit under test
    modify_cmd.handle_user_confirm("save as", mock_dev_env_local, mock_platform)

    # Check expectation
    mock_prompt.assert_called_once_with("Name of the new Development Environment")
    mock_platform.flush_descriptors.assert_called_once()

    assert "fake dev env" == mock_platform.local_dev_envs[0].name
    assert "test new name" == mock_platform.local_dev_envs[1].name

@patch("dem.cli.command.modify_cmd.typer.prompt")
def test_handle_user_confirm_save_as_already_exist(mock_prompt):
    # Test setup    
    mock_prompt.return_value = "test new name"
    mock_deserialized_local_dev_env = MagicMock()
    mock_platform = MagicMock()
    mock_platform.get_deserialized.return_value = mock_deserialized_local_dev_env
    mock_platform.get_dev_env_by_name.return_value = True
    mock_dev_env_local = MagicMock()
    mock_dev_env_local.name = "fake dev env"
    mock_platform.dev_envs = [mock_dev_env_local]
    
    # Run unit under test
    with pytest.raises(typer.Abort):
        modify_cmd.handle_user_confirm("save as", mock_dev_env_local, mock_platform)


def test_handle_user_confirm_cancel():
    # Test setup
    # Run unit under test
    with pytest.raises(typer.Abort):
        modify_cmd.handle_user_confirm("cancel", MagicMock(), MagicMock())

def test_execute_invalid_name():
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform
    mock_platform.get_dev_env_by_name.return_value = None
    test_dev_env_name =  "not existing env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["modify", test_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

    console = Console(file=io.StringIO())
    console.print("[red]The Development Environment doesn't exist.")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.modify_cmd.handle_user_confirm")
@patch("dem.cli.command.modify_cmd.get_confirm_from_user")
@patch("dem.cli.command.modify_cmd.get_modifications_from_user")
@patch("dem.cli.command.modify_cmd.get_tool_image_list")
def test_open_modify_panel(mock_get_tool_image_list, mock_get_modifications_from_user, 
                            mock_get_confirm_from_user, mock_handle_user_confirm):
    # Test setup
    mock_platform = MagicMock()
    mock_dev_env = MagicMock()

    mock_tool_images = MagicMock()
    mock_platform.tool_images = mock_tool_images

    mock_tool_image_list = MagicMock()
    mock_get_tool_image_list.return_value = mock_tool_image_list

    mock_confirmation = MagicMock()
    mock_get_confirm_from_user.return_value = mock_confirmation

    # Run unit under test
    modify_cmd.open_modify_panel(mock_platform, mock_dev_env)

    # Check expectations
    mock_get_tool_image_list.assert_called_once_with(mock_tool_images)
    mock_get_modifications_from_user.assert_called_once_with(mock_dev_env, 
                                                             mock_tool_image_list)
    mock_get_confirm_from_user.assert_called_once()
    mock_handle_user_confirm.assert_called_once_with(mock_confirmation, mock_dev_env, mock_platform)

def test_modify_single_tool_new_item() -> None:
    # Test setup
    mock_dev_env = MagicMock()
    mock_dev_env.tools = []
    mock_platform = MagicMock()
    test_tool_type = "test_tool_type"
    test_tool_image_name = "test_tool_image_name"
    test_tool_image_version = "test_tool_image_version"
    test_tool_image = test_tool_image_name + ":" + test_tool_image_version

    mock_platform.tool_images.registry.elements = [test_tool_image]

    # Run unit under test
    modify_cmd.modify_single_tool(mock_platform, mock_dev_env, test_tool_type,
                                  test_tool_image)

    # Check expectations
    assert mock_dev_env.tools[0]["type"] == test_tool_type
    assert mock_dev_env.tools[0]["image_name"] == test_tool_image_name
    assert mock_dev_env.tools[0]["image_version"] == test_tool_image_version

    mock_platform.container_engine.pull.assert_called_once_with(test_tool_image)
    mock_platform.flush_descriptors.assert_called_once()

def test_modify_single_tool_overwrite_item() -> None:
    # Test setup
    mock_dev_env = MagicMock()
    mock_dev_env.tools = [
        {
            "type": "test_tool_type",
            "image_name": "old_test_tool_image_name",
            "image_version": "old_test_tool_image_version"
        }
    ]
    mock_platform = MagicMock()
    test_tool_type = "test_tool_type"
    test_tool_image_name = "test_tool_image_name"
    test_tool_image_version = "test_tool_image_version"
    test_tool_image = test_tool_image_name + ":" + test_tool_image_version

    mock_platform.tool_images.registry.elements = [test_tool_image]

    # Run unit under test
    modify_cmd.modify_single_tool(mock_platform, mock_dev_env, test_tool_type,
                                  test_tool_image)

    # Check expectations
    assert mock_dev_env.tools[0]["type"] == test_tool_type
    assert mock_dev_env.tools[0]["image_name"] == test_tool_image_name
    assert mock_dev_env.tools[0]["image_version"] == test_tool_image_version

    mock_platform.container_engine.pull.assert_called_once_with(test_tool_image)
    mock_platform.flush_descriptors.assert_called_once()

@patch("dem.cli.command.modify_cmd.stderr.print")
def test_modify_single_tool_invalid_image(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_dev_env = MagicMock()
    mock_platform = MagicMock()
    test_tool_type = "test_tool_type"
    test_tool_image = "test_tool_image"

    mock_platform.tool_images.local.elements = []
    mock_platform.tool_images.registry.elements = []

    # Run unit under test
    modify_cmd.modify_single_tool(mock_platform, mock_dev_env, test_tool_type,
                                  test_tool_image)

    # Check expectations
    mock_platform.container_engine.pull.assert_not_called()
    mock_platform.flush_descriptors.assert_not_called()

    mock_stderr_print.assert_called_once_with(f"[red]Error: The {test_tool_image} is not an available image.[/]")

@patch("dem.cli.command.modify_cmd.stderr.print")
def test_modify_single_tool_no_image(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_dev_env = MagicMock()
    mock_platform = MagicMock()
    test_tool_type = "test_tool_type"
    test_tool_image = ""

    # Run unit under test
    modify_cmd.modify_single_tool(mock_platform, mock_dev_env, test_tool_type,
                                  test_tool_image)

    # Check expectations
    mock_platform.container_engine.pull.assert_not_called()
    mock_platform.flush_descriptors.assert_not_called()

    mock_stderr_print.assert_called_once_with("[red]Error: The tool type and the tool image must be set together.[/]")

@patch("dem.cli.command.modify_cmd.stderr.print")
def test_modify_single_tool_no_type(mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_dev_env = MagicMock()
    mock_platform = MagicMock()
    test_tool_type = ""
    test_tool_image = "test_tool_image"

    # Run unit under test
    modify_cmd.modify_single_tool(mock_platform, mock_dev_env, test_tool_type,
                                  test_tool_image)

    # Check expectations
    mock_platform.container_engine.pull.assert_not_called()
    mock_platform.flush_descriptors.assert_not_called()

    mock_stderr_print.assert_called_once_with("[red]Error: The tool type and the tool image must be set together.[/]")

@patch("dem.cli.command.modify_cmd.modify_single_tool")
@patch("dem.cli.command.modify_cmd.typer.confirm")
@patch("dem.cli.command.modify_cmd.stdout.print")
def test_execute_single_tool_dev_env_installed(mock_stdout_print: MagicMock, mock_confirm: MagicMock,
                                               mock_modify_single_tool: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env_name"
    test_tool_type = "test_tool_type"
    test_tool_image = "test_tool_image"
    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = True

    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run unit under test
    modify_cmd.execute(mock_platform, test_dev_env_name, test_tool_type, test_tool_image)

    # Check expectations
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stdout_print.assert_called_once_with("[yellow]The Development Environment is installed, so it can't be modified.[/]")
    mock_confirm.assert_called_once_with("Do you want to uninstall it first?", abort=True)
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_dev_env)
    mock_modify_single_tool.assert_called_once_with(mock_platform, mock_dev_env, test_tool_type, 
                                                    test_tool_image)

@patch("dem.cli.command.modify_cmd.open_modify_panel")
def test_execute_open_modify_panel(mock_open_modify_panel: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env_name"
    test_tool_type = ""
    test_tool_image = ""

    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = False
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run unit under test
    modify_cmd.execute(mock_platform, test_dev_env_name, test_tool_type, test_tool_image)

    # Check expectations
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_open_modify_panel.assert_called_once_with(mock_platform, mock_dev_env)