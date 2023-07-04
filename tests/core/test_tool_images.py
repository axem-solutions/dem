"""Tests for the tool_images.py"""
# tests/core/test_tool_images.py

# Unit under test:
import dem.core.tool_images as tool_images

# Test framework
from unittest.mock import patch, MagicMock, call

from dem.core.exceptions import RegistryError

def test_BaseToolImages():
    # Test setup
    test_container_engine = MagicMock()

    # Run unit under test
    base_tool_images = tool_images.BaseToolImages(test_container_engine)

    # Check expectations
    assert base_tool_images.container_egine is test_container_engine

@patch.object(tool_images.BaseToolImages, "__init__")
def test_LocalToolImages(mock_super__init__):
    # Test setup
    test_container_engine = MagicMock()
    mock_elements = MagicMock()
    test_container_engine.get_local_tool_images.return_value = mock_elements

    # Run unit under test
    local_tool_images = tool_images.LocalToolImages(test_container_engine)

    # Inject the test_container_engine for the registry_tool_images (super init is mocked).
    local_tool_images.container_egine = test_container_engine

    # Check expectations
    mock_super__init__.assert_called_once_with(test_container_engine)

    # Run unit under test
    local_tool_images.update()

    # Check expectations
    test_container_engine.get_local_tool_images.assert_called_once()
    assert local_tool_images.elements is mock_elements

@patch("dem.core.tool_images.registry.list_repos")
@patch.object(tool_images.BaseToolImages, "__init__")
def test_RegistryToolImages(mock_super__init__, mock_list_repos):
    # Test setup
    test_container_engine = MagicMock()
    mock_elements = MagicMock()
    mock_list_repos.return_value = mock_elements

    # Run unit under test
    registry_tool_images = tool_images.RegistryToolImages(test_container_engine)

    # Inject the test_container_engine for the registry_tool_images (super init is mocked).
    registry_tool_images.container_egine = test_container_engine

    # Check expectations
    mock_super__init__.assert_called_once_with(test_container_engine)

    # Run unit under test
    registry_tool_images.update()

    # Check expectations
    mock_list_repos.assert_called_once_with(test_container_engine, None, None)
    assert registry_tool_images.elements is mock_elements

@patch.object(tool_images.BaseToolImages, "__init__", MagicMock())
@patch("dem.core.tool_images.registry.list_repos")
def test_RegistryToolImages_RegistryError(mock_list_repos):
    # Test setup
    test_container_engine = MagicMock()
    mock_list_repos.side_effect = RegistryError()

    # Run unit under test
    registry_tool_images = tool_images.RegistryToolImages(test_container_engine)

    # Inject the test_container_engine for the registry_tool_images (super init is mocked).
    registry_tool_images.container_egine = test_container_engine

    registry_tool_images.update()

    # Check expectations
    mock_list_repos.assert_called_once_with(test_container_engine, None, None)
    assert not registry_tool_images.elements

@patch("dem.core.tool_images.RegistryToolImages")
@patch("dem.core.tool_images.LocalToolImages")
def test_ToolImages(mock_LocalToolImages, mock_RegistryToolImages):
    # Test setup
    test_container_engine = MagicMock()
    mock_local_tool_images = MagicMock()
    mock_LocalToolImages.return_value = mock_local_tool_images
    mock_registry_tool_images = MagicMock()
    mock_RegistryToolImages.return_value = mock_registry_tool_images

    # Run unit under test
    tool_images_obj = tool_images.ToolImages(test_container_engine)

    # Check expectations
    mock_local_tool_images.update.assert_called_once()
    mock_registry_tool_images.update.assert_called_once()

    assert tool_images_obj.local is mock_local_tool_images
    assert tool_images_obj.registry is mock_registry_tool_images