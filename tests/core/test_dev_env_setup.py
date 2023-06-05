"""Unit tests for the dev_env_setup."""
# tests/core/test_dev_env_setup.py

# Unit under test:
import dem.core.dev_env_setup as dev_env_setup

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call, PropertyMock

import tests.fake_data as fake_data
import json
from dem.core.exceptions import InvalidDevEnvJson
from dem.core.tool_images import ToolImages

@patch.object(dev_env_setup.DevEnvLocalSetup, "json", new_callable=PropertyMock)
def test_dev_env_json_with_invalid_tool_type_expect_error(mock_json_attribute):
    # Test setup
    mock_json = MagicMock()
    mock_json.read.return_value = json.loads(fake_data.invalid_dev_env_json)
    mock_json.deserialized = mock_json.read.return_value
    mock_json_attribute.return_value = mock_json

    with pytest.raises(InvalidDevEnvJson) as exported_exception_info:
        # Run unit under test
        dev_env_setup.DevEnvLocalSetup()

        # Check expectations
        excepted_error_message = "Error in dev_env.json: The following tool type is not supported: build_system" 
        assert str(exported_exception_info.value) == excepted_error_message

@patch("dem.core.dev_env_setup.__supported_dev_env_major_version__", 0)
@patch.object(dev_env_setup.DevEnvLocalSetup, "json", new_callable=PropertyMock)
def test_dev_env_json_with_invalid_version_expect_error(mock_json_attribute):
    # Test setup
    mock_json = MagicMock()
    mock_json.read.return_value = json.loads(fake_data.invalid_version_dev_env_json)
    mock_json.deserialized = mock_json.read.return_value
    mock_json_attribute.return_value = mock_json

    with pytest.raises(InvalidDevEnvJson) as exported_exception_info:
        # Run unit under test
        dev_env_setup.DevEnvLocalSetup()

        # Check expectations
        excepted_error_message = "Error in dev_env.json: The dev_env.json version v1.0 is not supported."
        assert str(exported_exception_info.value) == excepted_error_message

@patch("dem.core.dev_env_setup.__supported_dev_env_major_version__", 0)
@patch.object(dev_env_setup.DevEnvLocalSetup, "json", new_callable=PropertyMock)
def test_valid_dev_env_json_expect_no_error(mock_json_attribute):
    # Test setup
    mock_json = MagicMock()
    mock_json.read.return_value = json.loads(fake_data.dev_env_json)
    mock_json.deserialized = mock_json.read.return_value
    mock_json_attribute.return_value = mock_json

    # Run unit under test
    dev_env_setup.DevEnvLocalSetup()

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

def common_test_check_image_availability(mock_json_attribute: PropertyMock, with_update: bool) -> None:
    # Test setup
    mock_json = MagicMock()
    mock_json.read.return_value = json.loads(fake_data.dev_env_json)
    mock_json.deserialized = mock_json.read.return_value
    mock_json_attribute.return_value = mock_json

    test_dev_env_setup = dev_env_setup.DevEnvLocalSetup()
    test_dev_env = test_dev_env_setup.get_dev_env_by_name("demo")
    fake_tool_images = MagicMock(spec=ToolImages)
    fake_tool_images.elements = {
        "axemsolutions/make_gnu_arm:latest": ToolImages.LOCAL_AND_REGISTRY,
        "axemsolutions/stlink_org:latest": ToolImages.REGISTRY_ONLY
    }
    fake_tool_images.NOT_AVAILABLE = ToolImages.NOT_AVAILABLE

    # Run unit under test
    actual_image_statuses = test_dev_env.check_image_availability(fake_tool_images, 
                                                                  update_tool_images=with_update)

    # Check expectations
    if with_update == True:
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

@patch.object(dev_env_setup.DevEnvLocalSetup, "json", new_callable=PropertyMock)
def test_check_image_availability_without_update(mock_json_attribute):
    common_test_check_image_availability(mock_json_attribute, False)

@patch.object(dev_env_setup.DevEnvLocalSetup, "json", new_callable=PropertyMock)
def test_check_image_availability_with_update(mock_json_attribute):
    common_test_check_image_availability(mock_json_attribute, True)

@patch.object(dev_env_setup.DevEnvSetup, "__init__")
@patch.object(dev_env_setup.DevEnvLocalSetup, "json", new_callable=PropertyMock)
def test_DevEnvLocalSetup_core_cb_set(mock_json_attribute, mock_super_init):
    # Test setup
    mock_json = MagicMock()
    mock_json.read.return_value = MagicMock()
    mock_json.deserialized["development_environments"] = []
    mock_json.set_callback = MagicMock()
    mock_json_attribute.return_value = mock_json
    
    test_callback = MagicMock()

    # Run unit under test
    dev_env_setup.DevEnvLocalSetup.invalid_json_cb = test_callback
    test_dev_env_local_setup = dev_env_setup.DevEnvLocalSetup()

    # Check expectations
    mock_json.set_callback.assert_called_once_with(test_dev_env_local_setup.invalid_json_cb)
    mock_super_init.assert_called_once_with(mock_json.read.return_value)

@patch.object(dev_env_setup.DevEnvLocalSetup, "json", new_callable=PropertyMock)
def test_DevEnvLocalSetup_update_json(mock_json_attribute):
    # Test setup
    mock_json = MagicMock()
    mock_json.read.return_value = json.loads(fake_data.dev_env_json)
    mock_json.deserialized = mock_json.read.return_value
    mock_json_attribute.return_value = mock_json

    test_dev_env_local_setup = dev_env_setup.DevEnvLocalSetup()
    test_new_name = "new name"
    test_dev_env_local_setup.dev_envs[0].name = test_new_name
    expected_deserialized_json = mock_json.deserialized
    expected_deserialized_json["development_environments"][0]["name"] = test_new_name

    # Run unit under test
    test_dev_env_local_setup.update_json()

    # Check expectations
    test_dev_env_local_setup.json.write.assert_called_once_with(expected_deserialized_json)

@patch.object(dev_env_setup.DevEnvLocalSetup, "_container_engine", new_callable=PropertyMock)
@patch.object(dev_env_setup.DevEnvLocalSetup, "json", new_callable=PropertyMock)
def test_DevEnvLocalSetup_pull_images(mock_json_attribute, mock_container_engine_attribute):
    # Test setup
    mock_json = MagicMock()
    mock_json.read.return_value = json.loads(fake_data.dev_env_json)
    mock_json.deserialized = mock_json.read.return_value
    mock_json_attribute.return_value = mock_json

    mock_container_engine = MagicMock()
    mock_container_engine_attribute.return_value = mock_container_engine

    test_dev_env_local_setup = dev_env_setup.DevEnvLocalSetup()
    test_dev_env = test_dev_env_local_setup.dev_envs[0]

    for tool in test_dev_env.tools:
        tool["image_status"] = ToolImages.REGISTRY_ONLY

    # Run unit under test
    test_dev_env_local_setup.pull_images(test_dev_env.tools)

    # Check expectations
    pull_calls = []
    for tool in test_dev_env.tools:
        test_image_to_pull = tool["image_name"] + ":" + tool["image_version"]
        pull_calls.append(call(test_image_to_pull))

    test_dev_env_local_setup.container_engine.pull.assert_has_calls(pull_calls)