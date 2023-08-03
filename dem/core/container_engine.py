"""Docker container engine management."""
# dem/core/container_engine.py

from dem.core.core import Core
import docker

class ContainerEngine(Core):
    """ Operations on the Docker Container Engine."""

    def __init__(self) -> None:
        """ Init the class."""
        self._docker_client = docker.from_env()

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
        resp = self._docker_client.api.pull(repository, stream=True, decode=True)
        self.user_output.progress_generator(resp)

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
        for line in container.logs(stream=True):
            self.user_output.msg(line.decode().strip())

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