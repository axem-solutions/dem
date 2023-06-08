"""Unit tests for the main entry point of the CLI app."""
# tests/test__main__.py

# Unit under test
import dem.__main__ as __main__

# Test framework
import pytest
from unittest.mock import patch, MagicMock

from dem import __command__
from dem.core.exceptions import RegistryError
import docker.errors

@patch("dem.__main__.dem.cli.main.typer_cli")
def test_cli_success(mock_typer_cli):
    # Test setup

    # Run unit under test
    __main__.main()

    # Check expectations
    mock_typer_cli.assert_called_once_with(prog_name=__command__)

@patch("dem.__main__.stderr.print")
@patch("dem.__main__.dem.cli.main.typer_cli")
def test_cli_LookupError(mock_typer_cli, mock_stderr_print):
    # Test setup
    test_exception = "dummy"
    mock_typer_cli.side_effect = LookupError(test_exception)

    # Run unit under test
    __main__.main()

    # Check expectations
    mock_typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception + "[/]")

@patch("dem.__main__.stderr.print")
@patch("dem.__main__.dem.cli.main.typer_cli")
def test_cli_RegistryError(mock_typer_cli, mock_stderr_print):
    # Test setup
    test_exception = "dummy"
    mock_typer_cli.side_effect = RegistryError(test_exception)

    # Run unit under test
    __main__.main()

    # Check expectations
    mock_typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception + "[/]")

@patch("dem.__main__.stdout.print")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.dem.cli.main.typer_cli")
def test_cli_DockerException_permission_denied(mock_typer_cli, mock_stderr_print, mock_stdout_print):
    # Test setup
    test_exception = "Permission denied"
    mock_typer_cli.side_effect = docker.errors.DockerException(test_exception)

    # Run unit under test
    __main__.main()

    # Check expectations
    mock_typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception + "[/]")
    mock_stdout_print.assert_called_once_with("\nHint: Is your user part of the docker group?")

@patch("dem.__main__.stdout.print")
@patch("dem.__main__.stderr.print")
@patch("dem.__main__.dem.cli.main.typer_cli")
def test_cli_DockerException_unknown(mock_typer_cli, mock_stderr_print, mock_stdout_print):
    # Test setup
    test_exception = "unknown"
    mock_typer_cli.side_effect = docker.errors.DockerException(test_exception)

    # Run unit under test
    __main__.main()

    # Check expectations
    mock_typer_cli.assert_called_once_with(prog_name=__command__)
    mock_stderr_print.assert_called_once_with("[red]" + test_exception + "[/]")
    mock_stdout_print.assert_called_once_with("\nHint: Probably something is wrong with your Docker Engine installation. Try to reinstall it.")