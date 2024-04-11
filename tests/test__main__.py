"""Unit tests for the main entry point of the CLI app."""
# tests/test__main__.py

# Unit under test
import dem.__main__ as __main__

# Test framework
from unittest.mock import patch, MagicMock

from dem import __command__
from dem.core.exceptions import RegistryError
import docker.errors

@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_success(mock_Platform: MagicMock, mock_cli_main: MagicMock, mock_Core: MagicMock, 
                     mock_TUIUserOutput: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)

@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_LookupError(mock_Platform: MagicMock, mock_cli_main: MagicMock, mock_Core: MagicMock, 
                         mock_TUIUserOutput: MagicMock, mock_stderr_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "dummy"
    mock_cli_main.typer_cli.side_effect = LookupError(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception_text + "[/]")

@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_RegistryError(mock_Platform: MagicMock, mock_cli_main: MagicMock, mock_Core: MagicMock, 
                           mock_TUIUserOutput: MagicMock, mock_stderr_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "dummy"
    mock_cli_main.typer_cli.side_effect = RegistryError(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]Registry error: " + test_exception_text + "\nUsing local tool images only![/]")

@patch("dem.__main__.stdout.print")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_DockerException_permission_denied(mock_Platform: MagicMock, mock_cli_main: MagicMock, 
                                               mock_Core: MagicMock, mock_TUIUserOutput: MagicMock, 
                                               mock_stderr_print: MagicMock,
                                               mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "Permission denied"
    mock_cli_main.typer_cli.side_effect = docker.errors.DockerException(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception_text + "[/]")
    mock_stdout_print.assert_called_once_with("\nHint: Is your user part of the docker group?")

@patch("dem.__main__.stdout.print")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_DockerException_invalid_reference_format(mock_Platform: MagicMock, 
                                                      mock_cli_main: MagicMock, mock_Core: MagicMock, 
                                                      mock_TUIUserOutput: MagicMock, 
                                                      mock_stderr_print: MagicMock,
                                                      mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "invalid reference format"
    mock_cli_main.typer_cli.side_effect = docker.errors.DockerException(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception_text + "[/]")
    mock_stdout_print.assert_called_once_with("\nHint: The input repository might not exist in the registry.")

@patch("dem.__main__.stdout.print")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_DockerException_400(mock_Platform: MagicMock, mock_cli_main: MagicMock, 
                                 mock_Core: MagicMock, mock_TUIUserOutput: MagicMock, 
                                 mock_stderr_print: MagicMock, mock_stdout_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "400"
    mock_cli_main.typer_cli.side_effect = docker.errors.DockerException(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception_text + "[/]")
    mock_stdout_print.assert_called_once_with("\nHint: The input parameters might not be valid.")

@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_DockerException_unknown(mock_Platform: MagicMock, mock_cli_main: MagicMock, 
                                     mock_Core: MagicMock, mock_TUIUserOutput: MagicMock, 
                                     mock_stderr_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "unknown"
    mock_cli_main.typer_cli.side_effect = docker.errors.DockerException(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception_text + "[/]")

@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_ContainerEngineError(mock_Platform: MagicMock, mock_cli_main: MagicMock, 
                                  mock_Core: MagicMock, mock_TUIUserOutput: MagicMock, 
                                  mock_stderr_print: MagicMock):
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "unknown"
    mock_cli_main.typer_cli.side_effect = __main__.ContainerEngineError(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_cli_main.typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]Container engine error: " + test_exception_text + "[/]")

@patch("dem.__main__.stdout.print")
@patch("dem.__main__.typer.confirm")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_DataStorageError_invalid_config_file(mock_Platform: MagicMock, mock_cli_main: MagicMock, 
                                                  mock_Core: MagicMock, mock_TUIUserOutput: MagicMock, 
                                                  mock_stderr_print: MagicMock, 
                                                  mock_typer_confirm: MagicMock, 
                                                  mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "Invalid config.json!"
    mock_platform.config_file.update.side_effect = __main__.DataStorageError(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_stderr_print.assert_called_once_with(f"[red]Invalid file: {test_exception_text}[/]")
    mock_typer_confirm.assert_called_once_with("Do you want to reset the file?")
    mock_stdout_print.assert_called_once_with("Restoring the original configuration file...")
    mock_platform.config_file.restore.assert_called_once()

@patch("dem.__main__.stdout.print")
@patch("dem.__main__.typer.confirm")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.TUIUserOutput")
@patch("dem.__main__.Core")
@patch("dem.__main__.dem.cli.main")
@patch("dem.__main__.Platform")
def test_cli_DataStorageError_invalid_dev_env_desc(mock_Platform: MagicMock, mock_cli_main: MagicMock, 
                                                   mock_Core: MagicMock, mock_TUIUserOutput: MagicMock, 
                                                   mock_stderr_print: MagicMock, 
                                                   mock_typer_confirm: MagicMock, 
                                                   mock_stdout_print: MagicMock) -> None:
    # Test setup
    mock_platform = MagicMock()
    mock_Platform.return_value = mock_platform

    mock_tui_user_output = MagicMock()
    mock_TUIUserOutput.return_value = mock_tui_user_output
    test_exception_text = "Invalid dev_env.json!"
    mock_platform.config_file.update.side_effect = __main__.DataStorageError(test_exception_text)

    # Run unit under test
    __main__.main()

    # Check expectations
    assert mock_cli_main.platform is mock_platform

    mock_Platform.assert_called_once()
    mock_TUIUserOutput.assert_called_once()
    mock_Core.set_user_output.assert_called_once_with(mock_tui_user_output)
    mock_platform.config_file.update.assert_called_once()
    mock_stderr_print.assert_called_once_with(f"[red]Invalid file: {test_exception_text}[/]")
    mock_typer_confirm.assert_called_once_with("Do you want to reset the file?")
    mock_stdout_print.assert_called_once_with("Restoring the original Dev Env descriptor file...")
    mock_platform.dev_env_json.restore.assert_called_once()