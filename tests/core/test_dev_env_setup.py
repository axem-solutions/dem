"""Unit tests for the dev_env_setup."""
# tests/core/test_dev_env_setup.py

# Unit under test:
import dem.core.dev_env_setup as dev_env_setup

# Test framework
import pytest
from unittest.mock import patch, MagicMock

import tests.fake_data as fake_data
import json
from dem.core.exceptions import InvalidDevEnvJson
from dem.core.tool_images import ToolImages

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

def test_get_dev_env_by_name_match():
    # Test setup
    test_dev_env_setup = dev_env_setup.DevEnvSetup(json.loads(fake_data.dev_env_json))
    test_name = "dev_env_name"
    expected_dev_env = MagicMock()
    expected_dev_env.name = test_name
    test_dev_env_setup.dev_envs.append(expected_dev_env)

    # Run unit under test
    actual_dev_env = test_dev_env_setup.get_dev_env_by_name(test_name)

    # Check expectations
    assert actual_dev_env == expected_dev_env

def test_get_dev_env_by_name_no_match():
    # Test setup
    test_dev_env_setup = dev_env_setup.DevEnvSetup(json.loads(fake_data.dev_env_json))

    # Run unit under test
    actual_dev_env = test_dev_env_setup.get_dev_env_by_name("no_matching_name")

    # Check expectations
    assert actual_dev_env is None

def test_check_image_availability():
    # Test setup
    test_dev_env_setup = dev_env_setup.DevEnvLocalSetup(json.loads(fake_data.dev_env_json))
    test_dev_env = test_dev_env_setup.get_dev_env_by_name("demo")
    fake_tool_images = MagicMock(spec=ToolImages)
    fake_tool_images.elements = {
        "axemsolutions/make_gnu_arm:latest": ToolImages.LOCAL_AND_REGISTRY,
        "axemsolutions/stlink_org:latest": ToolImages.REGISTRY_ONLY
    }
    fake_tool_images.NOT_AVAILABLE = ToolImages.NOT_AVAILABLE

    # Run unit under test
    actual_image_statuses = test_dev_env.check_image_availability(fake_tool_images)

    # Check expectations
    fake_tool_images.update.assert_called_once()

    expected_image_statuses = [
        ToolImages.LOCAL_AND_REGISTRY,
        ToolImages.LOCAL_AND_REGISTRY,
        ToolImages.REGISTRY_ONLY,
        ToolImages.REGISTRY_ONLY,
        ToolImages.NOT_AVAILABLE
    ]
    assert expected_image_statuses == actual_image_statuses

    for idx, tool in enumerate(test_dev_env.tools):
        assert tool["image_status"] == expected_image_statuses[idx]
