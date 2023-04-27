"""Tests for the clone CLI command."""
# tests/cli/test_clone_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.clone_cmd as clone_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from rich.console import Console
import io

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test cases
def test_check_dev_env_to_clone_exist():
    # Test setup
    test_name = "dev_env_name"
    fake_dev_env = MagicMock()
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = fake_dev_env

    # Run unit under test
    actual_dev_env = clone_cmd.check_dev_env_to_clone_exist(dev_env_local_setup, test_name)

    # Check expectations
    assert actual_dev_env is None

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(test_name)

@patch("dem.cli.command.clone_cmd.stderr.print")
def test_check_dev_env_to_clone_not_exist(mock_stderr_print):
    # Test setup
    fake_name = "fake_env_name"
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = None

    # Run unit under test
    actual_dev_env = clone_cmd.check_dev_env_to_clone_exist(dev_env_local_setup, fake_name)

    # Check expectations
    assert False == actual_dev_env 

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(fake_name)
    mock_stderr_print.assert_called_once_with("[red]Error: The input Development Environment does not exist.[/]")

def test_check_new_dev_env_name_not_exist():
    # Test setup
    cloned_name = "dev_env_name"
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.get_dev_env_by_name.return_value = None

    # Run unit under test
    actual_dev_env = clone_cmd.check_new_dev_env_name_not_exist(dev_env_local_setup, cloned_name)

    # Check expectations
    assert actual_dev_env is True

    dev_env_local_setup.get_dev_env_by_name.assert_called_once_with(cloned_name)

def test_clone_given_dev_env():
    # Test setup
    test_name_to_clone = "dev_env_to_clone"    
    test_new_name = "test_cloned"
    fake_deserialized_dev_env_org_json = {
        "development_environments": [
            {
                "name": "dev_env_to_clone"
            }
        ]
    }

    # Run unit under test
    clone_cmd.clone_given_dev_env(fake_deserialized_dev_env_org_json, test_name_to_clone, test_new_name)

    # Check expectations    
    expected_deserialized_dev_env_org_json = {
        "development_environments": [
            {
                "name": "dev_env_to_clone"
            },
            {
                "name": "test_cloned"
            }
        ]
    }
    assert expected_deserialized_dev_env_org_json == fake_deserialized_dev_env_org_json

