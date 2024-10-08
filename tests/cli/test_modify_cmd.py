"""Tests for the modify command."""
# tests/cli/test_modify_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.modify_cmd as modify_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from rich.console import Console
import io, typer

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

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
    mock_platform.flush_dev_env_properties.assert_called_once()

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
    mock_platform.flush_dev_env_properties.assert_called_once()

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

def test_get_already_selected_tool_images() -> None:
    # Test setup
    mock_dev_env = MagicMock()
    mock_dev_env.tool_image_descriptors = [
        {"image_name": "test1", "image_version": "1.0"},
        {"image_name": "test2", "image_version": "2.0"}
    ]

    # Run unit under test
    actual_selected_tool_images = modify_cmd.get_already_selected_tool_images(mock_dev_env)

    # Check expectations
    expected_selected_tool_images = ["test1:1.0", "test2:2.0"]
    assert actual_selected_tool_images == expected_selected_tool_images

@patch("dem.cli.command.modify_cmd.stderr.print")
@patch("dem.cli.command.modify_cmd.typer.confirm")
def test_remove_missing_tool_images(mock_confirm: MagicMock, mock_stderr_print: MagicMock) -> None:
    # Test setup
    test_all_tool_images = {
        "test1:1.0": MagicMock(),
        "test2:2.0": MagicMock()
    }
    test_already_selected_tool_images = ["test1:1.0", "test2:2.0", "test3:3.0"]
    mock_confirm.side_effect = Exception("abort")
    
    # Run unit under test
    with pytest.raises(Exception):
        modify_cmd.remove_missing_tool_images(test_all_tool_images, test_already_selected_tool_images)

    # Check expectations
    assert "test3:3.0" not in test_already_selected_tool_images

    mock_stderr_print.assert_called_once_with("[red]The test3:3.0 is not available anymore.[/]")
    mock_confirm.assert_called_once_with("By continuing, the missing tool images will be removed from the Development Environment.",
                                         abort=True)

@patch("dem.cli.command.modify_cmd.DevEnvSettingsWindow")
def test_open_dev_env_settings_panel(mock_DevEnvSettingsWindow: MagicMock) -> None:
    # Test setup
    mock_dev_env_settings_panel = MagicMock()
    mock_DevEnvSettingsWindow.return_value = mock_dev_env_settings_panel
    expected_selected_tool_images = ["test1:1.0", "test2:2.0"]
    mock_dev_env_settings_panel.tool_image_menu.get_selected_tool_images.return_value = expected_selected_tool_images
    mock_dev_env_settings_panel.cancel_save_menu.get_selection.return_value = "save"

    mock_printable_tool_images = MagicMock()

    # Run unit under test
    actual_selected_tool_images = modify_cmd.open_dev_env_settings_panel(["test1:1.0", "test2:2.0"], 
                                                                         mock_printable_tool_images)

    # Check expectations
    assert actual_selected_tool_images == expected_selected_tool_images

    mock_DevEnvSettingsWindow.assert_called_once_with(mock_printable_tool_images, 
                                                     ["test1:1.0", "test2:2.0"])
    mock_dev_env_settings_panel.wait_for_user.assert_called_once()

@patch("dem.cli.command.modify_cmd.DevEnvSettingsWindow")
def test_open_dev_env_settings_panel_cancel(mock_DevEnvSettingsWindow: MagicMock) -> None:
    # Test setup
    mock_dev_env_settings_panel = MagicMock()
    mock_DevEnvSettingsWindow.return_value = mock_dev_env_settings_panel
    expected_selected_tool_images = ["test1:1.0", "test2:2.0"]
    mock_dev_env_settings_panel.selected_tool_images = expected_selected_tool_images
    mock_dev_env_settings_panel.cancel_save_menu.get_selection.return_value = "cancel"

    mock_printable_tool_images = MagicMock()

    # Run unit under test
    with pytest.raises(typer.Abort):
        modify_cmd.open_dev_env_settings_panel(["test1:1.0", "test2:2.0"], mock_printable_tool_images)

    # Check expectations
    mock_DevEnvSettingsWindow.assert_called_once_with(mock_printable_tool_images, 
                                                     ["test1:1.0", "test2:2.0"])
    mock_dev_env_settings_panel.wait_for_user.assert_called_once()

def test_update_dev_env() -> None:
    # Test setup
    mock_dev_env = MagicMock()
    mock_selected_tool_images = ["axem/test1:1.0", "test2:2.0"]

    # Run unit under test
    modify_cmd.update_dev_env(mock_dev_env, mock_selected_tool_images)

    # Check expectations
    expected_tool_image_descriptors = [
        {"image_name": "axem/test1", "image_version": "1.0"},
        {"image_name": "test2", "image_version": "2.0"}
    ]
    assert mock_dev_env.tool_image_descriptors == expected_tool_image_descriptors

@patch("dem.cli.command.modify_cmd.handle_user_confirm")
@patch("dem.cli.command.modify_cmd.get_confirm_from_user")
@patch("dem.cli.command.modify_cmd.update_dev_env")
@patch("dem.cli.command.modify_cmd.open_dev_env_settings_panel")
@patch("dem.cli.command.modify_cmd.convert_to_printable_tool_images")
@patch("dem.cli.command.modify_cmd.remove_missing_tool_images")
@patch("dem.cli.command.modify_cmd.get_already_selected_tool_images")
def test_modify_with_tui(mock_get_already_selected_tool_images: MagicMock,
                         mock_remove_missing_tool_images: MagicMock,
                         mock_convert_to_printable_tool_images: MagicMock,
                         mock_open_dev_env_settings_panel: MagicMock,
                         mock_update_dev_env: MagicMock,
                         mock_get_confirm_from_user: MagicMock,
                         mock_handle_user_confirm: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_dev_env = MagicMock()

    mock_already_selected_tool_images = MagicMock()
    mock_get_already_selected_tool_images.return_value = mock_already_selected_tool_images
    mock_printable_tool_images = MagicMock()
    mock_convert_to_printable_tool_images.return_value = mock_printable_tool_images
    mock_selected_tool_images = MagicMock()
    mock_open_dev_env_settings_panel.return_value = mock_selected_tool_images
    mock_confirmation = MagicMock()
    mock_get_confirm_from_user.return_value = mock_confirmation

    # Run unit under test
    modify_cmd.modify_with_tui(mock_platform, mock_dev_env)

    # Check expectations
    mock_get_already_selected_tool_images.assert_called_once_with(mock_dev_env)
    mock_remove_missing_tool_images.assert_called_once_with(mock_platform.tool_images.all_tool_images,
                                                            mock_already_selected_tool_images)
    mock_convert_to_printable_tool_images.assert_called_once_with(mock_platform.tool_images.all_tool_images)
    mock_open_dev_env_settings_panel.assert_called_once_with(mock_already_selected_tool_images, 
                                                             mock_printable_tool_images)
    mock_update_dev_env.assert_called_once_with(mock_dev_env, mock_selected_tool_images)
    mock_get_confirm_from_user.assert_called_once()
    mock_handle_user_confirm.assert_called_once_with(mock_confirmation, mock_dev_env, mock_platform)

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

    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

    console = Console(file=io.StringIO())
    console.print("[red]The Development Environment doesn't exist.")
    assert console.file.getvalue() == runner_result.stderr

@patch("dem.cli.command.modify_cmd.stdout.print")
@patch("dem.cli.command.modify_cmd.modify_with_tui")
def test_execute(mock_modify_with_tui: MagicMock, mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env_name"

    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = False
    mock_platform.get_tool_image_info_from_registries = False
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    # Run unit under test
    modify_cmd.execute(mock_platform, test_dev_env_name)

    # Check expectations
    assert mock_platform.get_tool_image_info_from_registries is True

    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_modify_with_tui.assert_called_once_with(mock_platform, mock_dev_env)
    mock_stdout_print.assert_called_once_with("[green]The Development Environment has been modified successfully![/]")

@patch("dem.cli.command.modify_cmd.modify_with_tui")
@patch("dem.cli.command.modify_cmd.typer.confirm")
@patch("dem.cli.command.modify_cmd.stdout.print")
def test_execute_installed(mock_stdout_print: MagicMock, mock_confirm: MagicMock,
                           mock_modify_with_tui: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env_name"

    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = True
    mock_platform.get_tool_image_info_from_registries = False
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env

    test_uninstall_dev_env_status = ["test_uninstall_dev_env_status", 
                                     "test_uninstall_dev_env_status2"]
    mock_platform.uninstall_dev_env.return_value = test_uninstall_dev_env_status

    # Run unit under test
    modify_cmd.execute(mock_platform, test_dev_env_name)

    # Check expectations
    assert mock_platform.get_tool_image_info_from_registries is True

    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stdout_print.assert_has_calls([
        call("[yellow]The Development Environment is installed, so it can't be modified.[/]"),
        call(test_uninstall_dev_env_status[0]), call(test_uninstall_dev_env_status[1]),
        call("[green]The Development Environment has been modified successfully![/]"),
    ])
    mock_confirm.assert_called_once_with("Do you want to uninstall it first?", abort=True)
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_dev_env)
    mock_modify_with_tui.assert_called_once_with(mock_platform, mock_dev_env)

@patch("dem.cli.command.modify_cmd.stderr.print")
@patch("dem.cli.command.modify_cmd.typer.confirm")
@patch("dem.cli.command.modify_cmd.stdout.print")
def test_execute_installed_PlatformError(mock_stdout_print: MagicMock, mock_confirm: MagicMock,
                                         mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    test_dev_env_name = "test_dev_env_name"
    mock_dev_env = MagicMock()
    mock_dev_env.is_installed = True
    mock_platform.get_tool_image_info_from_registries = False
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env
    test_exception_text = "test_exception_text"
    mock_platform.uninstall_dev_env.side_effect = modify_cmd.PlatformError(test_exception_text)

    # Run unit under test
    modify_cmd.execute(mock_platform, test_dev_env_name)

    # Check expectations
    assert mock_platform.get_tool_image_info_from_registries is True

    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_stdout_print.assert_called_once_with("[yellow]The Development Environment is installed, so it can't be modified.[/]")
    mock_confirm.assert_called_once_with("Do you want to uninstall it first?", abort=True)
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_dev_env)
    mock_stderr_print.assert_called_once_with(f"[red]Platform error: {test_exception_text}[/]")