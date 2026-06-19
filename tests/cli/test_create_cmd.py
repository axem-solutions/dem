"""Tests for the create CLI command."""

import dem.cli.main as main
import dem.core.commands.create_cmd as create_cmd

import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock, call, patch

runner = CliRunner(mix_stderr=False)


@patch("dem.core.commands.create_cmd.DevEnv")
def test_create_new_dev_env(mock_dev_env_class: MagicMock) -> None:
    mock_platform = MagicMock()
    mock_platform.local_dev_envs = []
    mock_platform.hosts = MagicMock()
    mock_dev_env = MagicMock()
    mock_dev_env_class.return_value = mock_dev_env
    descriptor = {"name": "test", "tools": []}

    create_cmd.create_new_dev_env(mock_platform, descriptor)

    mock_dev_env_class.assert_called_once_with(descriptor, mock_platform.hosts)
    mock_dev_env.assign_tool_image_instances.assert_called_once_with(mock_platform.tool_images)
    assert mock_platform.local_dev_envs == [mock_dev_env]


@patch("dem.core.commands.create_cmd.create_new_dev_env")
@patch("dem.core.commands.create_cmd.open_dev_env_settings_panel")
def test_create_dev_env_new(mock_open_panel: MagicMock, mock_create_new_dev_env: MagicMock) -> None:
    mock_platform = MagicMock()
    mock_platform.get_dev_env_by_name.return_value = None
    mock_open_panel.return_value = ["axemsolutions/make_gnu_arm:latest"]

    create_cmd.create_dev_env(mock_platform, "test-dev-env")

    mock_open_panel.assert_called_once_with(mock_platform.tool_images.all_tool_images)
    mock_create_new_dev_env.assert_called_once_with(
        mock_platform,
        {
            "name": "test-dev-env",
            "tools": [{"image_name": "axemsolutions/make_gnu_arm", "image_version": "latest"}],
            "custom_tasks": [],
            "docker_tasks": [],
            "run_tasks_as_current_user": False,
            "enable_docker_network": False,
            "installed": "False",
        },
    )


@patch("dem.core.commands.create_cmd.open_dev_env_settings_panel")
@patch("dem.core.commands.create_cmd.stdout.print")
@patch("dem.core.commands.create_cmd.typer.confirm")
def test_create_dev_env_overwrite_installed(
    mock_confirm: MagicMock,
    mock_stdout_print: MagicMock,
    mock_open_panel: MagicMock,
) -> None:
    mock_platform = MagicMock()
    mock_dev_env_original = MagicMock()
    mock_dev_env_original.is_installed = True
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env_original
    mock_platform.uninstall_dev_env.return_value = ["status1", "status2"]
    mock_open_panel.return_value = ["test/image:1.0"]

    create_cmd.create_dev_env(mock_platform, "test-dev-env")

    mock_confirm.assert_has_calls(
        [
            call("The input name is already used by a Development Environment. Overwrite it?", abort=True),
            call(
                "The Development Environment is installed, so it can't be overwritten. Uninstall it first?",
                abort=True,
            ),
        ]
    )
    mock_platform.uninstall_dev_env.assert_called_once_with(mock_dev_env_original)
    assert mock_dev_env_original.tool_image_descriptors == [
        {"image_name": "test/image", "image_version": "1.0"}
    ]
    mock_stdout_print.assert_has_calls([call("status1"), call("status2")])


@patch("dem.core.commands.create_cmd.stderr.print")
def test_create_dev_env_with_whitespace(mock_stderr_print: MagicMock) -> None:
    mock_platform = MagicMock()

    with pytest.raises(create_cmd.typer.Abort):
        create_cmd.create_dev_env(mock_platform, "test dev env")

    mock_stderr_print.assert_called_once_with(
        "The name of the Development Environment cannot contain whitespace characters!"
    )


@patch("dem.core.commands.create_cmd.stdout.print")
@patch("dem.core.commands.create_cmd.create_dev_env")
def test_execute(mock_create_dev_env: MagicMock, mock_stdout_print: MagicMock) -> None:
    mock_platform = MagicMock()
    mock_platform.get_tool_image_info_from_registries = False
    main.platform = mock_platform

    result = runner.invoke(main.typer_cli, ["create", "test-dev-env"], color=True)

    assert result.exit_code == 0
    assert mock_platform.get_tool_image_info_from_registries is True
    mock_platform.assign_tool_image_instances_to_all_dev_envs.assert_called_once()
    mock_create_dev_env.assert_called_once_with(mock_platform, "test-dev-env")
    mock_platform.flush_dev_env_properties.assert_called_once()
    mock_stdout_print.assert_has_calls(
        [
            call("The [green]test-dev-env[/] Development Environment has been created!"),
            call("Run [italic]dem install[/] to install it."),
        ]
    )
