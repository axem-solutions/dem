"""Tests for the cp CLI command."""
# tests/cli/test_cp_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.cp_cmd as cp_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
def test_check_dev_env_to_cp_exist():
    # Test setup
    test_name = "dev_env_name"
    fake_dev_env = MagicMock()
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env

    # Run unit under test
    actual_dev_env = cp_cmd.get_dev_env_to_cp(dev_env_local_setup, test_name)

    # Check expectations
    assert actual_dev_env is fake_dev_env

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_name)

@patch("dem.cli.command.cp_cmd.stderr.print")
def test_check_dev_env_to_cp_not_exist(mock_stderr_print):
    # Test setup
    fake_name = "fake_env_name"
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = None

    # Run unit under test
    actual_dev_env = cp_cmd.get_dev_env_to_cp(dev_env_local_setup, fake_name)

    # Check expectations
    assert actual_dev_env is None

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(fake_name)
    mock_stderr_print.assert_called_once_with("[red]Error: The input Development Environment does not exist.[/]")

def test_check_new_dev_env_name_not_taken():
    # Test setup
    cpd_name = "dev_env_name"
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = None

    # Run unit under test
    actual_dev_env = cp_cmd.check_new_dev_env_name_taken(dev_env_local_setup, cpd_name)

    # Check expectations
    assert actual_dev_env is False

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(cpd_name)

@patch("dem.cli.command.cp_cmd.stderr.print")
def test_check_new_dev_env_name_taken(mock_stderr_print):
    # Test setup
    cpd_name = "dev_env_name"
    dev_env_local_setup = MagicMock()
    fake_dev_env_to_cp = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env_to_cp

    # Run unit under test
    actual_dev_env = cp_cmd.check_new_dev_env_name_taken(dev_env_local_setup, cpd_name)

    # Check expectations
    assert actual_dev_env is True

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(cpd_name)
    mock_stderr_print.assert_called_once_with("[red]Error: Development environment already exists with the " + cpd_name + " name.[/]")

def test_cp_given_dev_env():
    # Test setup
    mock_platform = MagicMock()
    mock_dev_env_to_cp = MagicMock()
    mock_dev_env_to_cp.name = "test_dev_env"
    mock_dev_env_to_cp.is_installed = True

    test_new_name = "test_cpd"

    mock_platform.local_dev_envs = []

    # Run unit under test
    cp_cmd.cp_given_dev_env(mock_platform, mock_dev_env_to_cp, test_new_name)

    # Check expectations
    assert mock_platform.local_dev_envs[0].name is test_new_name
    assert mock_platform.local_dev_envs[0].is_installed is False

    mock_platform.flush_descriptors.assert_called_once()

@patch("dem.cli.command.cp_cmd.get_dev_env_to_cp")
@patch("dem.cli.command.cp_cmd.check_new_dev_env_name_taken")
@patch("dem.cli.command.cp_cmd.cp_given_dev_env")
def test_cp(mock_cp_given_dev_env, mock_check_new_dev_env_name_taken, 
               mock_get_dev_env_to_cp):
    # Test setup
    mock_platform = MagicMock()
    fake_dev_env_to_cp = MagicMock()
    mock_get_dev_env_to_cp.return_value = fake_dev_env_to_cp
    mock_check_new_dev_env_name_taken.return_value = False
    main.platform = mock_platform

    test_dev_env_to_cp_name = "test_dev_env_to_cp_name"
    test_new_dev_env_name = "test_new_dev_env_name"

    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, 
                                  ["cp", test_dev_env_to_cp_name, test_new_dev_env_name], 
                                  color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_get_dev_env_to_cp.assert_called_once_with(mock_platform, 
                                                      test_dev_env_to_cp_name)
    mock_check_new_dev_env_name_taken.assert_called_once_with(mock_platform, 
                                                              test_new_dev_env_name)
    mock_cp_given_dev_env.assert_called_once_with(mock_platform, 
                                                     fake_dev_env_to_cp, test_new_dev_env_name)