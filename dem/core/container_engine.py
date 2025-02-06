"""Docker container engine management."""
# dem/core/container_engine.py

from dem.core.core import Core
from dem.core.exceptions import ContainerEngineError
from docker import DockerClient
import docker.errors

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

    def run(self, container_arguments: list[str]) -> None:
        """ Run the container. 
        
            The function converts the Docker CLI commands to Docker Engine API call parameters.

            The container always gets started in detach mode. If the -d option is enabled the 
            function returns after the container has been started. If not enabled the DEM streams 
            the logs from the container to the user output while it is running. This effectively 
            results in the same behaviour as the docker run command's -d option.

            Args:
                container_arguments -- list of arguments to pass to the API call
        """
        container_arguments_iter = iter(container_arguments)

        image = ""
        ports = {}
        name = ""
        volumes = []
        command = ""
        privileged = False
        auto_remove = False
        stream_logs = True

        try:
            for argument in container_arguments_iter:
                if argument.startswith("-"):
                    match argument:
                        case "-p":
                            port_binding = next(container_arguments_iter)
                            try:
                                host_port, container_port = port_binding.split(":")
                            except ValueError:
                                raise ContainerEngineError("The option -p has invalid argument: " + port_binding)
                            ports[container_port] = int(host_port)
                        case "--name":
                            name = next(container_arguments_iter)
                        case "-v":
                            volumes.append(next(container_arguments_iter))
                        case "--privileged":
                            privileged = True
                        case "--rm":
                            auto_remove = True
                        case "-d":
                            stream_logs = False
                        case _:
                            raise ContainerEngineError("The input parameter " + argument + " is not supported!")
                else:
                    image = argument
                    for argument in container_arguments_iter:
                        command += argument + " "
                    command = command[:-1]
        except StopIteration:
            raise ContainerEngineError("Invalid input parameter!")

        run_result = self._docker_client.containers.run(image, command=command, 
                                                        auto_remove=auto_remove, 
                                                        privileged=privileged, volumes=volumes,
                                                        ports=ports, name=name, stderr=True, 
                                                        detach=True)

        if stream_logs:
            for line in run_result.logs(stream=True):
                self.user_output.msg(line.decode().strip())

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