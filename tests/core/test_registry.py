"""Unit tests for the registry."""
# tests/core/test_registry.py


import json

# Unit under test:
import dem.core.registry as registry
import dem.core.container_engine as container_engine

# Test framework
import pytest
from unittest.mock import patch, MagicMock


@patch("docker.from_env")
def test_list_repos(mock_docker_from_env):
    test_api_answer = [{'star_count': 0, 'is_official': False, 'name': 'axemsolutions/make_gnu_arm', 'is_automated': False, 'description': 'make:4.3;gnu_arm:10.3-2021.10'}]

    expected_images = ["axemsolutions/make_gnu_arm:latest"]

    mock_docker_client = MagicMock()
    mock_docker_client.images.search.return_value = test_api_answer    
    mock_docker_from_env.return_value = mock_docker_client
   
    container_engine_obj = container_engine.ContainerEngine()
    
    assert expected_images == registry.list_repos(container_engine_obj)

    
