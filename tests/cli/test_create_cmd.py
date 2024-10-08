"""Tests for the create CLI command."""
# tests/cli/test_create_cmd.py

# Unit under test
import dem.cli.main as main
import dem.cli.command.create_cmd as create_cmd

# Test framework
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call
from pytest import raises

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

@patch("dem.cli.command.create_cmd.DevEnvSettingsWindow")
@patch("dem.cli.command.create_cmd.convert_to_printable_tool_images")
def test_open_dev_env_settings_panel(mock_convert_to_printable_tool_images : MagicMock,
                                     mock_DevEnvSettingsWindow: MagicMock) -> None:
    # Test setup
    mock_all_tool_images = MagicMock()
    mock_printable_tool_images = MagicMock()
    mock_convert_to_printable_tool_images.return_value = mock_printable_tool_images

    mock_dev_env_settings_panel = MagicMock()
    mock_selected_tool_images = MagicMock()
    mock_dev_env_settings_panel.tool_image_menu.get_selected_tool_images.return_value = mock_selected_tool_images
    mock_DevEnvSettingsWindow.return_value = mock_dev_env_settings_panel

    mock_dev_env_settings_panel.cancel_save_menu.get_selection.return_value = "save"

    # Run unit under test
    actual_selected_tool_image_name = create_cmd.open_dev_env_settings_panel(mock_all_tool_images)

    # Check expectations
    assert actual_selected_tool_image_name is mock_selected_tool_images

    mock_convert_to_printable_tool_images.assert_called_once_with(mock_all_tool_images)
    mock_DevEnvSettingsWindow.assert_called_once_with(mock_printable_tool_images)
    mock_dev_env_settings_panel.wait_for_user.assert_called_once()
    mock_dev_env_settings_panel.cancel_save_menu.get_selection.assert_called_once()
    mock_dev_env_settings_panel.tool_image_menu.get_selected_tool_images.assert_called_once()

@patch("dem.cli.command.create_cmd.DevEnvSettingsWindow")
@patch("dem.cli.command.create_cmd.convert_to_printable_tool_images")
def test_open_dev_env_settings_panel_cancel(mock_convert_to_printable_tool_images: MagicMock,
                                            mock_DevEnvSettingsWindow: MagicMock) -> None:
    # Test setup
    mock_all_tool_images = MagicMock()
    mock_printable_tool_images = MagicMock()
    mock_convert_to_printable_tool_images.return_value = mock_printable_tool_images

    mock_dev_env_settings_panel = MagicMock()
    mock_selected_tool_images = MagicMock()
    mock_dev_env_settings_panel.selected_tool_images = mock_selected_tool_images
    mock_DevEnvSettingsWindow.return_value = mock_dev_env_settings_panel

    mock_dev_env_settings_panel.cancel_save_menu.get_selection.return_value = "cancel"

    # Run unit under test
    with raises(create_cmd.typer.Abort):
        create_cmd.open_dev_env_settings_panel(mock_all_tool_images)

    # Check expectations
    mock_convert_to_printable_tool_images.assert_called_once_with(mock_all_tool_images)
    mock_DevEnvSettingsWindow.assert_called_once_with(mock_printable_tool_images)
    mock_dev_env_settings_panel.wait_for_user.assert_called_once()
    mock_dev_env_settings_panel.cancel_save_menu.get_selection.assert_called_once()

def test_create_new_dev_env_descriptor() -> None:
    # Test setup
    test_dev_env_name = "test_dev_env"
    test_selected_tool_images = ["axemsolutions/make_gnu_arm:latest", "stlink_org:latest"]

    # Run unit under test
    actual_dev_env_descriptor = create_cmd.create_new_dev_env_descriptor(test_dev_env_name,
                                                                         test_selected_tool_images)
    
    # Check expectations
    expected_dev_env_descriptor = {
        "name": test_dev_env_name,
        "tools": [
            {
                "image_name": "axemsolutions/make_gnu_arm",
                "image_version": "latest"
            },
            {
                "image_name": "stlink_org",
                "image_version": "latest"
            }
        ]
    }
    
    assert expected_dev_env_descriptor == actual_dev_env_descriptor

@patch("dem.cli.command.create_cmd.DevEnv")
def test_create_new_dev_env(mock_DevEnv: MagicMock) -> None:
    # Test setup
    mock_new_dev_env = MagicMock()
    mock_DevEnv.return_value = mock_new_dev_env

    mock_platform = MagicMock()
    mock_platform.local_dev_envs = []
    mock_new_dev_env_descriptor = MagicMock()

    # Run unit under test
    create_cmd.create_new_dev_env(mock_platform, mock_new_dev_env_descriptor)

    # Check expectations
    assert mock_new_dev_env in mock_platform.local_dev_envs

    mock_DevEnv.assert_called_once_with(descriptor=mock_new_dev_env_descriptor)
    mock_new_dev_env.assign_tool_image_instances.assert_called_once_with(mock_platform.tool_images)

@patch("dem.cli.command.create_cmd.create_new_dev_env")
@patch("dem.cli.command.create_cmd.create_new_dev_env_descriptor")
@patch("dem.cli.command.create_cmd.open_dev_env_settings_panel")
def test_create_dev_env_new(mock_open_dev_env_settings_panel: MagicMock, 
                            mock_create_new_dev_env_descriptor: MagicMock,
                            mock_create_new_dev_env: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None

    mock_dev_env_descriptor = MagicMock()
    mock_create_new_dev_env_descriptor.return_value = mock_dev_env_descriptor

    mock_selected_tool_images = MagicMock()
    mock_open_dev_env_settings_panel.return_value = mock_selected_tool_images

    test_dev_env_name = "test_dev_env"

    # Run unit under test
    create_cmd.create_dev_env(mock_platform, test_dev_env_name)

    # Check expectations
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_open_dev_env_settings_panel.assert_called_once_with(mock_platform.tool_images.all_tool_images)
    mock_create_new_dev_env_descriptor.assert_called_once_with(test_dev_env_name,
                                                                mock_selected_tool_images)
    mock_create_new_dev_env.assert_called_once_with(mock_platform, mock_dev_env_descriptor)

@patch("dem.cli.command.create_cmd.create_new_dev_env_descriptor")
@patch("dem.cli.command.create_cmd.open_dev_env_settings_panel")
@patch("dem.cli.command.create_cmd.stdout.print")
@patch("dem.cli.command.create_cmd.typer.confirm")
def test_create_dev_env_overwrite_installed(mock_confirm: MagicMock, mock_stdout_print: MagicMock,
                                            mock_open_dev_env_settings_panel: MagicMock, 
                                            mock_create_new_dev_env_descriptor: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()

    fake_dev_env_descriptor = {}
    mock_tools = MagicMock()
    fake_dev_env_descriptor["tools"] = mock_tools
    mock_create_new_dev_env_descriptor.return_value = fake_dev_env_descriptor

    mock_dev_env_original = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env_original

    mock_selected_tool_images = MagicMock()
    mock_open_dev_env_settings_panel.return_value = mock_selected_tool_images

    test_uninstall_dev_env_status = ["status1", "status2"]
    mock_platform.uninstall_dev_env.return_value = test_uninstall_dev_env_status

    test_dev_env_name = "test_dev_env"

    # Run unit under test
    create_cmd.create_dev_env(mock_platform, test_dev_env_name)

    # Check expectations
    assert mock_dev_env_original.tool_image_descriptors is mock_tools

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_confirm.assert_has_calls([
        call("The input name is already used by a Development Environment. Overwrite it?", 
             abort=True),
        call("The Development Environment is installed, so it can't be overwritten. " + \
             "Uninstall it first?", abort=True)
    ])
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_dev_env_original)
    mock_stdout_print.assert_has_calls([
        call("status1"),
        call("status2")
    ])
    mock_open_dev_env_settings_panel.assert_called_once_with(mock_platform.tool_images.all_tool_images)
    mock_create_new_dev_env_descriptor.assert_called_once_with(test_dev_env_name, 
                                                               mock_selected_tool_images)

@patch("dem.cli.command.create_cmd.stderr.print")
@patch("dem.cli.command.create_cmd.typer.confirm")
def test_create_dev_env_overwrite_PlatformError(mock_confirm: MagicMock, 
                                                mock_stderr_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_dev_env_original = MagicMock()
    mock_dev_env_original.is_installed = True
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env_original
    test_exception_text = "test_exception_text"
    mock_platform.uninstall_dev_env.side_effect = create_cmd.PlatformError(test_exception_text)

    test_dev_env_name = "test_dev_env"

    # Run unit under test
    with pytest.raises(create_cmd.typer.Abort):
        create_cmd.create_dev_env(mock_platform, test_dev_env_name)

    # Check expectations
    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_confirm.assert_has_calls([
        call("The input name is already used by a Development Environment. Overwrite it?", 
             abort=True),
        call("The Development Environment is installed, so it can't be overwritten. " + \
             "Uninstall it first?", abort=True)
    ])
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_dev_env_original)
    mock_stderr_print.assert_called_once_with(f"[red]Platform error: {test_exception_text}[/]")

@patch("dem.cli.command.create_cmd.typer.confirm")
def test_create_dev_env_abort(mock_confirm: MagicMock) -> None:
    # Test setup
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_original = MagicMock()
    mock_dev_env_local_setup.get_dev_env_by_name.return_value = mock_dev_env_original
    mock_confirm.side_effect = Exception()
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    # The exception doesn't metter, only the fact that the function execution has stopped.
    with pytest.raises(Exception):
        create_cmd.create_dev_env(mock_dev_env_local_setup, expected_dev_env_name)

    # Check expectations
    mock_dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(expected_dev_env_name)
    mock_confirm.assert_called_once_with("The input name is already used by a Development Environment. Overwrite it?",
                                        abort=True)

@patch("dem.cli.command.create_cmd.stdout.print")
@patch("dem.cli.command.create_cmd.create_dev_env")
def test_execute(mock_create_dev_env: MagicMock, mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_platform.get_tool_image_info_from_registries = False
    expected_dev_env_name = "test_dev_env"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", expected_dev_env_name], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code
    assert mock_platform.get_tool_image_info_from_registries is True

    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_create_dev_env.assert_called_once_with(mock_platform, expected_dev_env_name)
    mock_platform.flush_dev_env_properties.assert_called_once()
    mock_stdout_print.assert_has_calls([
        call(f"The [green]{expected_dev_env_name}[/] Development Environment has been created!"),
        call("Run [italic]dem install[/] to install it.")
    ])

@patch("dem.cli.command.create_cmd.stderr.print")
def test_create_dev_env_with_whitespace(mock_stderr_print):
    # Test setup
    mock_dev_env_local_setup = MagicMock()
    mock_dev_env_local_setup.get_dev_env_by_name.return_value = None

    mock_tool_images = MagicMock()
    mock_dev_env_local_setup.tool_images = mock_tool_images

    expected_dev_env_name = "test dev env with space"

    # Run unit under test
    with pytest.raises(create_cmd.typer.Abort):
        create_cmd.create_dev_env(mock_dev_env_local_setup, expected_dev_env_name)

    # Check expectations
    mock_dev_env_local_setup.get_dev_env_by_name.assert_not_called()
    mock_stderr_print.assert_called_once_with("The name of the Development Environment cannot contain whitespace characters!")