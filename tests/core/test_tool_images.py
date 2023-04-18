"""Tests for the tool_images.py"""
# tests/core/test_tool_images.py

# Unit under test:
from dem.core.tool_images import ToolImages

# Test framework
import pytest
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

    assert actual_tool_images.elements["local_only_image:latest"] == ToolImages.LOCAL_ONLY
    assert actual_tool_images.elements["registry_only_image:latest"] == ToolImages.REGISTRY_ONLY
    assert actual_tool_images.elements["local_and_registry_image:latest"] == ToolImages.LOCAL_AND_REGISTRY