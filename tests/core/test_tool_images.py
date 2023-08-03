"""Tests for the tool_images.py"""
# tests/core/test_tool_images.py

# Unit under test:
import dem.core.tool_images as tool_images

# Test framework
from unittest.mock import patch, MagicMock
import pytest

from dem.core.exceptions import RegistryError

def test_LocalToolImages():
    # Test setup
    test_container_engine = MagicMock()
    mock_elements = MagicMock()
    test_container_engine.get_local_tool_images.return_value = mock_elements

    # Run unit under test
    local_tool_images = tool_images.LocalToolImages(test_container_engine)
    local_tool_images.update()

    # Check expectations
    test_container_engine.get_local_tool_images.assert_called_once()
    assert local_tool_images.elements is mock_elements

def test_RegistryToolImages():
    # Test setup
    test_registries = MagicMock()
    mock_elements = MagicMock()
    test_registries.list_repos.return_value = mock_elements

    # Run unit under test
    registry_tool_images = tool_images.RegistryToolImages(test_registries)
    registry_tool_images.update()

    # Check expectations
    test_registries.list_repos.assert_called_once()
    assert registry_tool_images.elements is mock_elements

def test_RegistryToolImages_RegistryError():
    # Test setup
    test_registries = MagicMock()
    test_registries.list_repos.side_effect = RegistryError()

    # Run unit under test
    with pytest.raises(Exception):
        registry_tool_images = tool_images.RegistryToolImages(test_registries)
        registry_tool_images.update()

        # Check expectations
        test_registries.list_repos.assert_called_once()
        assert not registry_tool_images.elements

@patch("dem.core.tool_images.RegistryToolImages")
@patch("dem.core.tool_images.LocalToolImages")
def test_ToolImages(mock_LocalToolImages: MagicMock, mock_RegistryToolImages: MagicMock):
    # Test setup
    mock_container_engine = MagicMock()
    mock_registries = MagicMock()
    mock_local_tool_images = MagicMock()
    mock_LocalToolImages.return_value = mock_local_tool_images
    mock_registry_tool_images = MagicMock()
    mock_RegistryToolImages.return_value = mock_registry_tool_images

    # Run unit under test
    tool_images_obj = tool_images.ToolImages(mock_container_engine, mock_registries)

    # Check expectations
    mock_LocalToolImages.assert_called_once_with(mock_container_engine)
    mock_RegistryToolImages.assert_called_once_with(mock_registries)

    mock_local_tool_images.update.assert_called_once()
    mock_registry_tool_images.update.assert_called_once()

    assert tool_images_obj.local is mock_local_tool_images
    assert tool_images_obj.registry is mock_registry_tool_images