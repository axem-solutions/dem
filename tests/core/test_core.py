"""Unit test for the core."""
# tests/core/test_core.py

# Unit under test:
import dem.core.core as core

# Test framework
from unittest.mock import MagicMock, patch
import pytest

@pytest.fixture
def tear_down_test():
    yield
    core.Core.set_user_output(core.NoUserOutput())

def test_Core(tear_down_test) -> None:
    # Test setup
    mock_user_output = MagicMock()
    
    # Run unit under test
    test_core = core.Core()

    # Check expectations
    assert isinstance(test_core.user_output, core.NoUserOutput)
    assert isinstance(test_core.config_file, core.ConfigFile)

    # Run unit under test
    core.Core.set_user_output(mock_user_output)

    # Check expectations
    assert test_core.user_output is mock_user_output