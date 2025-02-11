"""Docker container engine management."""
# dem/core/container_engine.py

from dem.core.core import Core
from dem.core.exceptions import ContainerEngineError
from docker import DockerClient
from docker.models.containers import Container
import docker.errors
from typing import Any

class ContainerEngine(Core):
    """ Operations on the Docker Container Engine."""

    def __init__(self, docker_server_url: str) -> None:
        """ Init the class."""
        self._docker_client: DockerClient | None = None
        self._docker_server_url: str = docker_server_url
    
    def start(self) -> None:
        """ Start the Docker client.

            Raises:
                ContainerEngineError -- if the Docker client can't be started
        """
        if self._docker_client is None:
            try:
                self._docker_client = DockerClient(base_url=self._docker_server_url, version="auto")
            except docker.errors.DockerException as e:
                raise ContainerEngineError(f"Unable to connect to the Docker Engine: {e}")

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

    def run(self, image: str, command: str | list | None = None, stdout: bool = True, 
            stderr: bool = True, remove: bool = True, **kwargs: dict[str, Any]) -> None:
        """ Run the container. 
        
            The container always gets started in detach mode. If the -d option is enabled the 
            function returns after the container has been started. If not enabled DEM streams 
            the logs from the container to the user output while it is running. This effectively 
            results in the same behaviour as the docker run command's -d option.

            Args:
                image -- the image to run
                command -- the command to run in the container
                stdout -- stream stdout
                stderr -- stream stderr
                remove -- remove the container after it has stopped
                kwargs -- additional arguments - see the docker-py documentation for more details
        """
        # Run the container in detached mode
        container: Container = self._docker_client.containers.run(image, command, detach=True, stdout=True, stderr=True,
                                                                  **kwargs)

        # Attach to the container's logs and stream them in real-time
        for line in container.logs(stdout=stdout, stderr=stderr, stream=True):
            self.user_output.msg(line.decode().strip())

        # Remove the container if the remove option is enabled
        if remove:
            container.remove()

    def remove(self, image: str) -> None:
        """ Remove a tool image.

            Args: 
                image -- the tool image to remove

            Raises:
                ContainerEngineError -- if the image is used by a container
        """
        try:
            self._docker_client.images.remove(image)
        except docker.errors.ImageNotFound:
            self.user_output.msg(f"[yellow]The {image} doesn't exist. Unable to remove it.[/]\n")
        except docker.errors.APIError:
            raise ContainerEngineError(f"The {image} is used by a container. Unable to remove it.\n")

    def create_network(self, network_name: str) -> None:
        """ Create a Docker network.

            Args:
                network_name -- the name of the network
        """
        self._docker_client.networks.create(network_name)

    def remove_network(self, network_name: str) -> None:
        """ Remove a Docker network.

            Args:
                network_name -- the name of the network
        """
        try:
            network = self._docker_client.networks.get(network_name)
        except docker.errors.NotFound:
            self.user_output.msg(f"[yellow]The {network_name} doesn't exist. Unable to remove it.[/]\n")
            return

        network.remove()