"""Tests for the create CLI command."""
# tests/cli/test_create_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test helpers
## Test cases

def test_select_tool_menu():
    # Run unit under test
    runner_result = runner.invoke(main.typer_cli, ["create", "test_dev_env"], color=True)

    # Check expectations
    assert 0 == runner_result.exit_code