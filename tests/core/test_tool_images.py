"""Tests for the tool_images.py"""
# tests/core/test_tool_images.py

# Unit under test:
from dem.core.tool_images import ToolImages

# Test framework
from unittest.mock import patch, MagicMock

@patch("dem.core.tool_images.container_engine.ContainerEngine")
@patch("dem.core.tool_images.registry.list_repos")
def test_init(mock_list_repos, mock_ContainerEngine):
    # Test setup
    test_local_images = [
        "local_only_image:latest",
        "local_and_registry_image:latest"
    ]
    test_registry_images = [
        "registry_only_image:latest",
        "local_and_registry_image:latest"
    ]
    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    fake_container_engine.get_local_tool_images.return_value = test_local_images
    mock_list_repos.return_value = test_registry_images

    # Run unit under test
    actual_tool_images = ToolImages()

    # Check expectations
    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called_once()
    mock_list_repos.assert_called_once()

    expected_elements = {
        "local_only_image:latest": ToolImages.LOCAL_ONLY,
        "registry_only_image:latest": ToolImages.REGISTRY_ONLY,
        "local_and_registry_image:latest": ToolImages.LOCAL_AND_REGISTRY
    }

    assert actual_tool_images.elements == expected_elements

@patch("dem.core.tool_images.container_engine.ContainerEngine")
@patch("dem.core.tool_images.registry.list_repos")
def test_rerun_update(mock_list_repos, mock_ContainerEngine):
    # Test setup
    test_local_images = [
        [
            "local_only_image_before_update:latest",
            "local_and_registry_image_before_update:latest"
        ],
        [
            "local_only_image_after_update:latest",
            "local_and_registry_image_after_update:latest"
        ]
    ]
    test_registry_images = [
        [
            "registry_only_image_before_update:latest",
            "local_and_registry_image_before_update:latest"
        ],
        [
            "registry_only_image_after_update:latest",
            "local_and_registry_image_after_update:latest"
        ]
    ]
    fake_container_engine = MagicMock()
    mock_ContainerEngine.return_value = fake_container_engine
    fake_container_engine.get_local_tool_images.side_effect = test_local_images
    mock_list_repos.side_effect = test_registry_images

    # Run unit under test
    actual_tool_images = ToolImages()
    actual_tool_images.update()

    # Check expectations
    mock_ContainerEngine.assert_called_once()
    fake_container_engine.get_local_tool_images.assert_called()
    mock_list_repos.assert_called_with(fake_container_engine)

    expected_elements = {
        "local_only_image_after_update:latest": ToolImages.LOCAL_ONLY,
        "registry_only_image_after_update:latest": ToolImages.REGISTRY_ONLY,
        "local_and_registry_image_after_update:latest": ToolImages.LOCAL_AND_REGISTRY
    }

    assert actual_tool_images.elements == expected_elements