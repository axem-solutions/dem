"""Tests for the tool_images.py"""
# tests/core/test_tool_images.py

# Unit under test:
import dem.core.tool_images as tool_images

# Test framework
from unittest.mock import MagicMock
import pytest

def test_ToolImage() -> None:
    # Run unit under test
    tool_image = tool_images.ToolImage("test_repo:test_tag")

    # Check expectations
    assert tool_image.name == "test_repo:test_tag"
    assert tool_image.repository == "test_repo"
    assert tool_image.tag == "test_tag"
    assert tool_image.availability == tool_images.ToolImage.NOT_AVAILABLE

def test_ToolImage_InvalidName() -> None:
    # Test setup 
    test_name = "test_repo"

    # Run unit under test
    with pytest.raises(tool_images.ToolImageError) as e:
        tool_images.ToolImage(test_name)

    # Check expectations
    assert str(e.value) == f"Invalid tool image name: {test_name}"

def test_ToolImages_update() -> None:
    # Test setup
    mock_container_engine = MagicMock()
    mock_registries = MagicMock()
    test_local_tool_images = ["local_tool_image_1:tag", 
                              "local_tool_image_2:tag", 
                              "local_and_registry_tool_image:tag"]
    test_registry_tool_images = ["registry_tool_image_1:tag", 
                                 "registry_tool_image_2:tag", 
                                 "local_and_registry_tool_image:tag"]

    mock_container_engine.get_local_tool_images.return_value = test_local_tool_images
    mock_registries.list_repos.return_value = test_registry_tool_images

    tool_images_instance = tool_images.ToolImages(mock_container_engine, mock_registries)
    tool_images_instance.all_tool_images = {
        "local_tool_image_1:tag": tool_images.ToolImage("local_tool_image_1:tag"),
        "registry_tool_image_1:tag": tool_images.ToolImage("registry_tool_image_1:tag"),
        "local_and_registry_tool_image:tag": tool_images.ToolImage("local_and_registry_tool_image:tag")
    }

    # Run unit under test
    tool_images_instance.update(True, True)

    # Check expectations
    assert len(tool_images_instance.all_tool_images) == 5
    assert tool_images_instance.all_tool_images["local_tool_image_1:tag"].availability == tool_images.ToolImage.LOCAL_ONLY
    assert tool_images_instance.all_tool_images["local_tool_image_2:tag"].availability == tool_images.ToolImage.LOCAL_ONLY
    assert tool_images_instance.all_tool_images["registry_tool_image_1:tag"].availability == tool_images.ToolImage.REGISTRY_ONLY
    assert tool_images_instance.all_tool_images["registry_tool_image_2:tag"].availability == tool_images.ToolImage.REGISTRY_ONLY
    assert tool_images_instance.all_tool_images["local_and_registry_tool_image:tag"].availability == tool_images.ToolImage.LOCAL_AND_REGISTRY

    mock_container_engine.get_local_tool_images.assert_called_once()
    mock_registries.list_repos.assert_called_once()

def test_ToolImages_get_local_ones() -> None:
    # Test setup
    mock_container_engine = MagicMock()
    mock_registries = MagicMock()
    test_local_tool_images = ["local_tool_image_1:tag", 
                              "local_tool_image_2:tag", 
                              "local_and_registry_tool_image:tag"]
    test_registry_tool_images = ["registry_tool_image_1:tag", 
                                 "registry_tool_image_2:tag", 
                                 "local_and_registry_tool_image:tag"]

    mock_container_engine.get_local_tool_images.return_value = test_local_tool_images
    mock_registries.list_repos.return_value = test_registry_tool_images

    tool_images_instance = tool_images.ToolImages(mock_container_engine, mock_registries)
    tool_images_instance.update(True, True)

    # Run unit under test
    local_tool_images = tool_images_instance.get_local_ones()

    # Check expectations
    assert len(local_tool_images) == 3
    assert "local_tool_image_1:tag" in local_tool_images
    assert "local_tool_image_2:tag" in local_tool_images
    assert "local_and_registry_tool_image:tag" in local_tool_images

    mock_container_engine.get_local_tool_images.assert_called_once()
    mock_registries.list_repos.assert_called_once()

def test_ToolImages_get_registry_ones() -> None:
    # Test setup
    mock_container_engine = MagicMock()
    mock_registries = MagicMock()
    test_local_tool_images = ["local_tool_image_1:tag", 
                              "local_tool_image_2:tag", 
                              "local_and_registry_tool_image:tag"]
    test_registry_tool_images = ["registry_tool_image_1:tag", 
                                 "registry_tool_image_2:tag", 
                                 "local_and_registry_tool_image:tag"]

    mock_container_engine.get_local_tool_images.return_value = test_local_tool_images
    mock_registries.list_repos.return_value = test_registry_tool_images

    tool_images_instance = tool_images.ToolImages(mock_container_engine, mock_registries)
    tool_images_instance.update(True, True)

    # Run unit under test
    registry_tool_images = tool_images_instance.get_registry_ones()

    # Check expectations
    assert len(registry_tool_images) == 3
    assert "registry_tool_image_1:tag" in registry_tool_images
    assert "registry_tool_image_2:tag" in registry_tool_images
    assert "local_and_registry_tool_image:tag" in registry_tool_images

    mock_container_engine.get_local_tool_images.assert_called_once()
    mock_registries.list_repos.assert_called_once()