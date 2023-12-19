"""Unit tests for the Dev Env."""
# tests/core/test_dev_env.py

# Unit under test:
import dem.core.dev_env as dev_env

# Test framework
from unittest.mock import MagicMock

def test_DevEnv():
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "installed": "True",
        "tools": [MagicMock()]
    }

    # Run unit under test
    test_dev_env = dev_env.DevEnv(test_descriptor)

    # Check expectations
    assert test_dev_env.name is test_descriptor["name"]
    assert test_dev_env.tools is test_descriptor["tools"]

    # Test setup
    mock_base_dev_env = MagicMock()
    mock_base_dev_env.name = "test_name"
    mock_base_dev_env.tools = [MagicMock()]

    # Run unit under test
    test_dev_env = dev_env.DevEnv(dev_env_to_copy=mock_base_dev_env)

    # Check expectations
    assert test_dev_env.name is mock_base_dev_env.name
    assert test_dev_env.tools is mock_base_dev_env.tools


def test_DevEnv_check_image_availability():
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "installed": "True",
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

    
    mock_tool_images.local.update.assert_called_once()
    mock_tool_images.registry.update.assert_called_once()


def test_DevEnv_check_image_availability_local_only():
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "installed": "True",
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

    
    mock_tool_images.local.update.assert_called_once()

def test_DevEnv_get_registry_only_tool_images() -> None:
    # Test setup
    test_descriptor = {
        "name": "test_name",
        "installed": "False",
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
    actual_registry_onnly_tool_images = test_dev_env.get_registry_only_tool_images(mock_tool_images, True)

    # Check expectations
    expected_registry_only_tool_images = {
        "test_image_name3:test_image_tag3",
    }
    assert expected_registry_only_tool_images == actual_registry_onnly_tool_images