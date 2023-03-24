"""Tests for the pull CLI command."""
# tests/cli/test_pull_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

## Global test variables
## Test helpers
## Test cases

def test_dev_env_not_available_in_org():
