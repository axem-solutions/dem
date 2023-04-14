"""Tests for the rename CLI command."""
# tests/cli/test_rename_cmd.py

# Unit under test:
import dem.cli.main as main
import dem.cli.command.rename_cmd as rename_cmd

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, call

from rich.console import Console
import io

## Test cases
def test_dev_env_name_check_match():
    # Test setup
    test_name = "dev_env_name"
    expected_dev_env = MagicMock()
    expected_dev_env.name = test_name
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.dev_envs = []
    dev_env_local_setup.dev_envs.append(expected_dev_env)

    # Run unit under test
    actual_dev_env = rename_cmd.dev_env_name_check(dev_env_local_setup, test_name)

    # Check expectations
    assert actual_dev_env == expected_dev_env

def test_dev_env_name_check_no_match():
    # Test setup
    test_name = "dev_env_name"
    fake_dev_env = MagicMock()
    fake_dev_env.name = test_name
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.dev_envs = []
    dev_env_local_setup.dev_envs.append(fake_dev_env)

    # Run unit under test
    actual_dev_env = rename_cmd.dev_env_name_check(dev_env_local_setup, "no_matching_name")

    # Check expectations
    assert actual_dev_env is None

def test_check_dev_env_name_exist():
    # Test setup
    test_name = "dev_env_name"
    fake_dev_env = MagicMock()
    fake_dev_env.name = test_name
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.dev_envs = []
    dev_env_local_setup.dev_envs.append(fake_dev_env)

    # Run unit under test
    actual_dev_env = rename_cmd.check_dev_env_name_exist(dev_env_local_setup,test_name)

    # Check expectations
    assert actual_dev_env is None

def test_check_dev_env_name_exist():
    # Test setup
    test_name = "dev_env_name"
    fake_name = "fake_env_name"
    fake_dev_env = MagicMock()
    fake_dev_env.name = test_name
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.dev_envs = []
    dev_env_local_setup.dev_envs.append(fake_dev_env)

    # Run unit under test
    actual_dev_env = rename_cmd.check_dev_env_name_exist(dev_env_local_setup,fake_name)

    # Check expectations
    assert -1 == actual_dev_env 

def test_rename_given_dev_env_error():
    # Test setup
    test_name = "dev_env_name"    
    fake_dev_env = MagicMock()
    fake_dev_env.name = test_name
    dev_env_local_setup = MagicMock()
    dev_env_local_setup.dev_envs = []
    dev_env_local_setup.dev_envs.append(fake_dev_env)

    fake_deserialized_dev_env_org_json = MagicMock()

    # Run unit under test
    actual_dev_env = rename_cmd.rename_given_dev_env(fake_deserialized_dev_env_org_json,dev_env_local_setup,test_name)

    # Check expectations
    assert  -1 == actual_dev_env 
