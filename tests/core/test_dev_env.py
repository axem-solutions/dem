"""Unit tests for the Dev Env."""
# tests/core/test_dev_env.py

# Unit under test:
import dem.core.dev_env as dev_env

# Test framework
import pytest
from unittest.mock import patch, MagicMock, call, PropertyMock

@patch.object(dev_env.DevEnv, "_check_tool_type_support")
def test_DevEnv(mock__check_tool_type_support: MagicMock):
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "tools": [MagicMock()]
    }

    # Run unit under test
    test_dev_env = dev_env.DevEnv(test_descriptor)

    # Check expectations
    assert test_dev_env.name is test_descriptor["name"]
    assert test_dev_env.tools is test_descriptor["tools"]

    mock__check_tool_type_support.assert_called_once_with(test_descriptor)

    # Test setup
    mock_base_dev_env = MagicMock()
    mock_base_dev_env.name = "test_name"
    mock_base_dev_env.tools = [MagicMock()]

    # Run unit under test
    test_dev_env = dev_env.DevEnv(dev_env_to_copy=mock_base_dev_env)

    # Check expectations
    assert test_dev_env.name is mock_base_dev_env.name
    assert test_dev_env.tools is mock_base_dev_env.tools

@patch.object(dev_env.DevEnv, "__init__")
def test_DevEnv__check_tool_type_support(mock___init__: MagicMock):
    # Test setup
    test_descriptor = {
        "tools": [
            {
                "type": "invalid type"
            }
        ]
    }

    mock___init__.return_value = None

    test_dev_env = dev_env.DevEnv(test_descriptor)

    with pytest.raises(dev_env.InvalidDevEnvJson) as e:
        # Run unit under test
        test_dev_env._check_tool_type_support(test_descriptor)

        # Check expectations
        assert str(e) == "The following tool type is not supported: " + test_descriptor["tools"][0]["type"]

        mock___init__.assert_called_once()

@patch.object(dev_env.DevEnv, "_check_tool_type_support")
def test_DevEnv_check_image_availability(mock__check_tool_type_support: MagicMock):
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "tools": [
            {
                "image_name": "test_image_name1",
                "image_version": "test_image_tag1"
            },
            {
                "image_name": "test_image_name2",
                "image_version": "test_image_tag2"
            },
            {
                "image_name": "test_image_name3",
                "image_version": "test_image_tag3"
            },
            {
                "image_name": "test_image_name4",
                "image_version": "test_image_tag4"
            },
        ]
    }
    mock_tool_images = MagicMock()
    mock_tool_images.local.elements = [
        "test_image_name1:test_image_tag1",
        "test_image_name2:test_image_tag2"
    ]
    mock_tool_images.registry.elements = [
        "test_image_name1:test_image_tag1",
        "test_image_name3:test_image_tag3"
    ]
    test_dev_env = dev_env.DevEnv(test_descriptor)

    # Run unit under test
    actual_image_statuses = test_dev_env.check_image_availability(mock_tool_images, True)

    # Check expectations
    expected_statuses = [
        dev_env.ToolImages.LOCAL_AND_REGISTRY,
        dev_env.ToolImages.LOCAL_ONLY,
        dev_env.ToolImages.REGISTRY_ONLY,
        dev_env.ToolImages.NOT_AVAILABLE
    ]
    assert expected_statuses == actual_image_statuses
    for idx, tool in enumerate(test_dev_env.tools):
        assert expected_statuses[idx] == tool["image_status"]

    mock__check_tool_type_support.assert_called_once()
    mock_tool_images.local.update.assert_called_once()
    mock_tool_images.registry.update.assert_called_once()

@patch.object(dev_env.DevEnv, "_check_tool_type_support")
def test_DevEnv_check_image_availability_local_only(mock__check_tool_type_support: MagicMock):
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "tools": [
            {
                "image_name": "test_image_name1",
                "image_version": "test_image_tag1"
            },
            {
                "image_name": "test_image_name2",
                "image_version": "test_image_tag2"
            },
            {
                "image_name": "test_image_name3",
                "image_version": "test_image_tag3"
            },
            {
                "image_name": "test_image_name4",
                "image_version": "test_image_tag4"
            },
        ]
    }
    mock_tool_images = MagicMock()
    mock_tool_images.local.elements = [
        "test_image_name1:test_image_tag1",
        "test_image_name2:test_image_tag2"
    ]
    test_dev_env = dev_env.DevEnv(test_descriptor)

    # Run unit under test
    actual_image_statuses = test_dev_env.check_image_availability(mock_tool_images, True, True)

    # Check expectations
    expected_statuses = [
        dev_env.ToolImages.LOCAL_ONLY,
        dev_env.ToolImages.LOCAL_ONLY,
        dev_env.ToolImages.NOT_AVAILABLE,
        dev_env.ToolImages.NOT_AVAILABLE
    ]
    assert expected_statuses == actual_image_statuses
    for idx, tool in enumerate(test_dev_env.tools):
        assert expected_statuses[idx] == tool["image_status"]

    mock__check_tool_type_support.assert_called_once()
    mock_tool_images.local.update.assert_called_once()