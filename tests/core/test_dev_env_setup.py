"""Unit tests for the dev_env_setup."""
# tests/core/test_dev_env_setup.py

# Unit under test:
import dem.core.dev_env_setup as dev_env_setup

# Test framework
import pytest
from unittest.mock import patch

import tests.fake_data as fake_data
import json
from dem.core.exceptions import InvalidDevEnvJson

def test_dev_env_json_with_invalid_tool_type_expect_error():
    excepted_error_message = "Error in dev_env.json: The following tool type is not supported: build_system" 

    with pytest.raises(InvalidDevEnvJson) as exported_exception_info:
        invaid_deserialized_dev_env_json = json.loads(fake_data.invalid_dev_env_json)
        dev_env_setup.DevEnvLocalSetup(invaid_deserialized_dev_env_json)
    assert str(exported_exception_info.value) == excepted_error_message

@patch("dem.core.dev_env_setup.__supported_dev_env_major_version__", 0)
def test_dev_env_json_with_invalid_version_expect_error():
    excepted_error_message = "Error in dev_env.json: The dev_env.json version v1.0 is not supported."

    with pytest.raises(InvalidDevEnvJson) as exported_exception_info:
        dev_env_setup.DevEnvLocalSetup(json.loads(fake_data.invalid_version_dev_env_json))
    assert str(exported_exception_info.value) == excepted_error_message

@patch("dem.core.dev_env_setup.__supported_dev_env_major_version__", 0)
def test_valid_dev_env_json_expect_no_error():
    dev_env_setup.DevEnvLocalSetup(json.loads(fake_data.dev_env_json))

def test_get_valid_dev_env_org_from_setup_by_name():
    # Run unit under test
    dev_env_org_setup = dev_env_setup.DevEnvOrgSetup(json.loads(fake_data.dev_env_org_json))
    dev_env_org = dev_env_org_setup.get_dev_env("demo")

    # Check expectations
    assert dev_env_org.name == "demo"

def test_get_invalid_dev_env_org_from_setup_by_name():
    # Run unit under test
    dev_env_org_setup = dev_env_setup.DevEnvOrgSetup(json.loads(fake_data.dev_env_org_json))
    dev_env_org = dev_env_org_setup.get_dev_env("invalid")

    # Check expectations
    assert dev_env_org == None