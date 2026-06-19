"""Unit tests for the main entry point."""

import dem.__main__ as main_module

from unittest.mock import MagicMock, patch

import docker.errors

from dem import __command__
from dem.core.exceptions import RegistryError


def build_platform_mock() -> MagicMock:
    platform = MagicMock()
    platform.api_server.server.started = False
    return platform


@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_main_success(
    mock_platform_class: MagicMock,
    mock_cli_main: MagicMock,
    mock_core: MagicMock,
    mock_tui_user_output_class: MagicMock,
) -> None:
    mock_platform = build_platform_mock()
    mock_platform_class.return_value = mock_platform

    main_module.main()

    assert mock_cli_main.platform is mock_platform
    mock_core.set_user_output.assert_called_once_with(mock_tui_user_output_class.return_value)
    mock_platform.configure.assert_called_once()
    mock_platform.load_dev_envs.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)


@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_main_handles_lookup_error(
    mock_platform_class: MagicMock,
    mock_cli_main: MagicMock,
    mock_core: MagicMock,
    mock_tui_user_output_class: MagicMock,
    mock_stderr_print: MagicMock,
) -> None:
    mock_platform = build_platform_mock()
    mock_platform_class.return_value = mock_platform
    mock_cli_main.typer_cli.side_effect = LookupError("missing")

    main_module.main()

    mock_stderr_print.assert_called_once_with("[red]missing[/]")


@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_main_handles_registry_error(
    mock_platform_class: MagicMock,
    mock_cli_main: MagicMock,
    mock_core: MagicMock,
    mock_tui_user_output_class: MagicMock,
    mock_stderr_print: MagicMock,
) -> None:
    mock_platform = build_platform_mock()
    mock_platform_class.return_value = mock_platform
    mock_cli_main.typer_cli.side_effect = RegistryError("broken")

    main_module.main()

    mock_stderr_print.assert_called_once_with("[red]Registry error: broken[/]")


@patch("dem.__main__.stdout.print")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_main_handles_docker_exception_with_permission_hint(
    mock_platform_class: MagicMock,
    mock_cli_main: MagicMock,
    mock_core: MagicMock,
    mock_tui_user_output_class: MagicMock,
    mock_stderr_print: MagicMock,
    mock_stdout_print: MagicMock,
) -> None:
    mock_platform = build_platform_mock()
    mock_platform_class.return_value = mock_platform
    mock_cli_main.typer_cli.side_effect = docker.errors.DockerException("Permission denied")

    main_module.main()

    mock_stderr_print.assert_called_once_with("[red]Permission denied[/]")
    mock_stdout_print.assert_called_once_with("\nHint: Is your user part of the docker group?")


@patch("dem.__main__.stdout.print")
@patch("dem.__main__.typer.confirm")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_main_restores_config_on_data_storage_error(
    mock_platform_class: MagicMock,
    mock_cli_main: MagicMock,
    mock_core: MagicMock,
    mock_tui_user_output_class: MagicMock,
    mock_stderr_print: MagicMock,
    mock_typer_confirm: MagicMock,
    mock_stdout_print: MagicMock,
) -> None:
    mock_platform = build_platform_mock()
    mock_platform_class.return_value = mock_platform
    mock_platform.configure.side_effect = main_module.DataStorageError("config.json broken")
    mock_typer_confirm.return_value = True

    main_module.main()

    mock_stderr_print.assert_called_once_with("[red]Invalid file: config.json broken[/]")
    mock_typer_confirm.assert_called_once_with("Do you want to reset the file?")
    mock_stdout_print.assert_called_once_with("Restoring the original configuration file...")
    mock_platform.config_file.restore.assert_called_once()


@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_main_stops_api_server_if_started(
    mock_platform_class: MagicMock,
    mock_cli_main: MagicMock,
    mock_core: MagicMock,
    mock_tui_user_output_class: MagicMock,
) -> None:
    mock_platform = build_platform_mock()
    mock_platform.api_server.server.started = True
    mock_platform_class.return_value = mock_platform

    main_module.main()

    mock_platform.api_server.stop.assert_called_once()
