"""Docker container engine management."""
# dem/core/container_engine.py

from typing import Callable
from types import MethodType
import docker

class ContainerEngine():
    """ Operations on the Docker Container Engine."""

    def __init__(self) -> None:
        """ Init the class."""
        self._docker_client = docker.from_env()
        self._pull_progress_cb = None
        self._msg_cb = None

    def get_local_tool_images(self) -> list[str]:
        """ Get local tool images.
        
        Return with the list of the locally avialable tool image names.
        """
        local_image_tags = []

        for image in self._docker_client.images.list():
            for tag in image.tags:
                if tag:
                    local_image_tags.append(tag)

        return local_image_tags

    def pull(self, repository: str) -> None:
        """ Pull a repository from the axemsolutions registry.
        
        Args:
            repository -- repository to pull
        """
        if self._pull_progress_cb:
            resp = self._docker_client.api.pull(repository, stream=True, decode=True)
            self._pull_progress_cb(generator=resp)
        else:
            self._docker_client.api.pull(repository)

    def run(self, image: str, workspace_path: str, command: str, privileged: bool) -> None:
        """ Run the image with the given command and directory to mount.
        
        Args:
            image -- container image to run
            workspace_path -- workspace path
            command -- command to be passed to the assigned tool image
            priviliged -- give extended priviliges to the container
        """
        volume_binds = [workspace_path + ":/work"]
        container = self._docker_client.containers.run(image, command=command, auto_remove=True, 
                                                       privileged=privileged, stderr=True, 
                                                       volumes=volume_binds, detach=True)
        if self._msg_cb is not None:
            for line in container.logs(stream=True):
                self._msg_cb(msg=line.decode().strip())

    def remove(self, image: str) -> None:
        """ Remove a tool image.
        
        Args: 
            image -- the tool image to remove
        """
        self._docker_client.images.remove(image)

    def search(self, registry: str) -> list[str]:
        """ Search repository in the axemsolutions registry.
        
        Args:
            registry -- registry to search
        """
        local_registryimagelist = []

        for repositories in self._docker_client.images.search(registry):
            local_registryimagelist.append(repositories['name'])

        return local_registryimagelist

    def set_pull_progress_cb(self, pull_progress_callback: Callable) -> None:
        """ Register the callback function for the pull command's progress.
        
        Args:
            pull_progress_callback -- function to call with the new pull progress
        """
        self._pull_progress_cb = MethodType(pull_progress_callback, self)

    def set_msg_cb(self, msg_callback: Callable) -> None:
        """ Register the callback function for sending generic messages for the user.
        
        Args:
            msg_callback -- function to call with the message
        """
        self._msg_cb = MethodType(msg_callback, self)
