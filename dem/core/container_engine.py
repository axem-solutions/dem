"""Docker container engine management."""
# dem/core/container_engine.py

from typing import Callable
from types import MethodType
import docker

import dem.cli.core_cb as core_cb

class ContainerEngine():
    def __init__(self) -> None:
        """Operations on the Docker Container Engine."""
        self._docker_client = docker.from_env()
        self._docker_api_client = docker.APIClient(base_url="unix:///var/run/docker.sock", 
                                                   version="auto")
        self._pull_progress_cb = None

    def get_local_tool_images(self) -> list[str]:
        """Get local tool images.
        
        Return with the list of the locally avialable tool image names.
        """
        local_image_tags = []

        for image in self._docker_client.images.list():
            for tag in image.tags:
                if tag:
                    local_image_tags.append(tag)

        return local_image_tags

    def pull(self, repository: str) -> None:
        """Pull a repository from the axemsolutions registry.
        
        Args:
            repository -- repository to pull"""
        if self._pull_progress_cb:
            resp = self._docker_api_client.pull(repository, stream=True, decode=True)
            self._pull_progress_cb(generator=resp)
        else:
            self._docker_api_client.pull(repository)

    def remove(self, image: str) -> None:
        """Remove a tool image.
        
        Args: 
            image -- the tool image to remove"""
        self._docker_client.images.remove(image)

    def search(self, registry: str) -> None:
        """Search repository in the axemsolutions registry.
        
        Args:
            registry -- registry to search"""
        local_registryimagelist = []

        for repositories in self._docker_client.images.search(registry):        
            local_registryimagelist.append(repositories['name'])
        return local_registryimagelist

    def set_pull_progress_cb(self, pull_progress_callback: Callable) -> None:
        self._pull_progress_cb = MethodType(pull_progress_callback, self)
