"""Unit tests for the dev_env_setup."""
# tests/core/test_dev_env_setup.py

# Unit under test:
import dem.core.dev_env as dev_env

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call, PropertyMock

import tests.fake_data as fake_data
import json
from dem.core.exceptions import InvalidDevEnvJson
from dem.core.tool_images import ToolImages

@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
def test_dev_env_json_with_invalid_tool_type_expect_error(mock_LocalDevEnvJSON: MagicMock):
    # Test setup
    mock_json = MagicMock()
    mock_LocalDevEnvJSON.return_value = mock_json
    mock_json.deserialized = json.loads(fake_data.invalid_dev_env_json)

    with pytest.raises(InvalidDevEnvJson) as exported_exception_info:
        # Run unit under test
        dev_env.DevEnvLocalSetup()

        # Check expectations
        excepted_error_message = "Error in dev_env.json: The following tool type is not supported: build_system" 
        assert str(exported_exception_info.value) == excepted_error_message

@patch("dem.core.dev_env_setup.__supported_dev_env_major_version__", 0)
@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
def test_dev_env_json_with_invalid_version_expect_error(mock_LocalDevEnvJSON: MagicMock):
    # Test setup
    mock_json = MagicMock()
    mock_LocalDevEnvJSON.return_value = mock_json
    mock_json.deserialized = json.loads(fake_data.invalid_version_dev_env_json)

    with pytest.raises(InvalidDevEnvJson) as exported_exception_info:
        # Run unit under test
        dev_env.DevEnvLocalSetup()

        # Check expectations
        excepted_error_message = "Error in dev_env.json: The dev_env.json version v1.0 is not supported."
        assert str(exported_exception_info.value) == excepted_error_message

@patch("dem.core.dev_env_setup.__supported_dev_env_major_version__", 0)
@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
def test_valid_dev_env_json_expect_no_error(mock_LocalDevEnvJSON: MagicMock):
    # Test setup
    mock_json = MagicMock()
    mock_LocalDevEnvJSON.return_value = mock_json
    mock_json.deserialized = json.loads(fake_data.dev_env_json)

    # Run unit under test
    dev_env.DevEnvLocalSetup()

def test_get_dev_env_by_name_match():
    # Test setup
    test_dev_env_setup = dev_env.DevEnvSetup(json.loads(fake_data.dev_env_json))
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
    test_dev_env_setup = dev_env.DevEnvSetup(json.loads(fake_data.dev_env_json))

    # Run unit under test
    actual_dev_env = test_dev_env_setup.get_dev_env_by_name("no_matching_name")

    # Check expectations
    assert actual_dev_env is None

def common_test_check_image_availability(mock_LocalDevEnvJSON: MagicMock, with_update: bool,
                                         local_only: bool) -> None:
    # Test setup
    mock_json = MagicMock()
    mock_LocalDevEnvJSON.return_value = mock_json
    mock_json.deserialized = json.loads(fake_data.dev_env_json)

    test_dev_env_setup = dev_env.DevEnvLocalSetup()
    test_dev_env = test_dev_env_setup.get_dev_env_by_name("demo")
    mock_tool_images = MagicMock()
    mock_tool_images.local.elements = [
        "axemsolutions/make_gnu_arm:latest",
    ]
    mock_tool_images.registry.elements = [
        "axemsolutions/make_gnu_arm:latest",
        "axemsolutions/stlink_org:latest",
    ]

    # Run unit under test
    actual_image_statuses = test_dev_env.check_image_availability(mock_tool_images, 
                                                                  update_tool_images=with_update,
                                                                  local_only=local_only)

    # Check expectations
    if with_update == True:
        mock_tool_images.local.update.assert_called_once()
        if local_only is False:
            mock_tool_images.registry.update.assert_called_once()

    if local_only is False:
        expected_image_statuses = [
            ToolImages.LOCAL_AND_REGISTRY,
            ToolImages.LOCAL_AND_REGISTRY,
            ToolImages.REGISTRY_ONLY,
            ToolImages.REGISTRY_ONLY,
            ToolImages.NOT_AVAILABLE
        ]
    else:
        expected_image_statuses = [
            ToolImages.LOCAL_ONLY,
            ToolImages.LOCAL_ONLY,
            ToolImages.NOT_AVAILABLE,
            ToolImages.NOT_AVAILABLE,
            ToolImages.NOT_AVAILABLE
        ]
    assert expected_image_statuses == actual_image_statuses

    for idx, tool in enumerate(test_dev_env.tools):
        assert tool["image_status"] == expected_image_statuses[idx]

@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
def test_check_image_availability_without_update(mock_LocalDevEnvJSON: MagicMock):
    common_test_check_image_availability(mock_LocalDevEnvJSON, False, False)

@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
def test_check_image_availability_with_update(mock_LocalDevEnvJSON: MagicMock):
    common_test_check_image_availability(mock_LocalDevEnvJSON, True, False)

@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
def test_check_image_availability_with_update_and_local_only(mock_LocalDevEnvJSON: MagicMock):
    common_test_check_image_availability(mock_LocalDevEnvJSON, True, True)

@patch.object(dev_env.DevEnvSetup, "get_deserialized")
@patch.object(dev_env.DevEnvSetup, "__init__")
@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
def test_DevEnvLocalSetup_flush_to_file(mock_LocalDevEnvJSON: MagicMock, 
                                        mock_super__init__: MagicMock, 
                                        mock_get_deserialized: MagicMock):
    # Test setup
    mock_json = MagicMock()
    mock_json.deserialized = {
        "development_environments": []
    }
    mock_LocalDevEnvJSON.return_value = mock_json
    mock_get_deserialized.return_value = mock_json.deserialized

    test_local_platform = dev_env.DevEnvLocalSetup()

    # Run unit under test
    test_local_platform.flush_to_file()

    # Check expectations
    assert test_local_platform.json.deserialized is mock_json.deserialized

    mock_super__init__.assert_called_once_with(mock_json.deserialized)
    mock_get_deserialized.assert_called_once()
    mock_json.flush.assert_called_once()

@patch.object(dev_env.Core, "user_output")
@patch.object(dev_env.DevEnvLocalSetup, "_container_engine", new_callable=PropertyMock)
@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
def test_DevEnvLocalSetup_pull_images(mock_LocalDevEnvJSON: MagicMock, 
                                      mock_container_engine_attribute: MagicMock,
                                      mock_user_output: MagicMock):
    # Test setup
    mock_json = MagicMock()
    mock_json.read.return_value = json.loads(fake_data.dev_env_json)
    mock_json.deserialized = mock_json.read.return_value
    mock_LocalDevEnvJSON.return_value = mock_json

    mock_container_engine = MagicMock()
    mock_container_engine_attribute.return_value = mock_container_engine

    test_dev_env_local_setup = dev_env.DevEnvLocalSetup()
    test_dev_env = test_dev_env_local_setup.dev_envs[0]

    for tool in test_dev_env.tools:
        tool["image_status"] = ToolImages.REGISTRY_ONLY

    # Run unit under test
    test_dev_env_local_setup.pull_images(test_dev_env.tools)

    # Check expectations
    msg_calls = [
        call("\nPulling image axemsolutions/cpputest:latest", is_title=True),
        call("\nPulling image axemsolutions/make_gnu_arm:latest", is_title=True),
        call("\nPulling image axemsolutions/stlink_org:latest", is_title=True),
    ]
    mock_user_output.msg.assert_has_calls(msg_calls, any_order=True)

    pull_calls = [
        call("axemsolutions/cpputest:latest"),
        call("axemsolutions/make_gnu_arm:latest"),
        call("axemsolutions/stlink_org:latest"),
    ]
    test_dev_env_local_setup.container_engine.pull.assert_has_calls(pull_calls, any_order=True)

@patch("dem.core.dev_env_setup.LocalDevEnvJSON")
@patch.object(dev_env.DevEnvLocalSetup, "_container_engine", new_callable=PropertyMock)
@patch.object(dev_env.DevEnvSetup, "__init__")
def test_DevEnvLocalSetup_run_container(mock_super__init__, mock_container_engine_attribute, 
                                        mock_LocalDevEnvJSON: MagicMock):
    # Test setup
    test_tool_image = "test_tool_image"
    test_workspace_path = "test_workspace_path"
    test_command = "test_command"
    test_privileged = False
    mock_container_engine = MagicMock()
    mock_container_engine_attribute.return_value = mock_container_engine
    mock_json = MagicMock()
    mock_json.deserialized = {
        "development_environments": []
    }
    mock_LocalDevEnvJSON.return_value = mock_json

    test_dev_env_local_setup = dev_env.DevEnvLocalSetup()

    # Run unit under test
    test_dev_env_local_setup.run_container(test_tool_image, test_workspace_path, test_command, 
                                           test_privileged)

    # Check expectations
    mock_super__init__.assert_called_once_with(mock_json.deserialized)
    mock_container_engine.run.assert_called_once_with(test_tool_image, test_workspace_path, 
                                                      test_command, test_privileged)