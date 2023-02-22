"""Unit tests for the dev_env_setup."""
# tests/core/test_dev_env_setup.py

# Unit under test:
import dem.core.dev_env_setup as dev_env_setup

import pytest
import tests.fake_data as fake_data
import json
from dem.core.exceptions import InvalidDevEnvJson

def test_invalid_dev_env_json_expect_error():
    with pytest.raises(LookupError):
        invaid_deserialized_dev_env_json = json.loads(fake_data.invalid_dev_env_json)
        dev_env_setup.DevEnvSetup(invaid_deserialized_dev_env_json)
    assert "Error in dev_env.json. The following tool type is not supported: build_system"