""" This module contains the different task types. """
# dem/core/task.py

from dem.core.hosts import Hosts
from dem.core.exceptions import TaskError

class Task():
    """ A Task. """
    def __init__(self, task_descriptor: dict) -> None:
        """ Initialize the Task class.
        
            Args:
                task_descriptor -- The description of the task.
        """
        self.descriptor: dict = task_descriptor

class DockerTask(Task):
    """ A Docker Task. """
    def __init__(self, task_descriptor: dict, hosts: Hosts) -> None:
        """ Initialize the DockerTask class.
        
            Args:
                task_descriptor -- The description of the task.
                hosts -- The available hosts.
        """
        super().__init__(task_descriptor)
        self.name: str = task_descriptor["name"]
        self.rm: bool = task_descriptor["rm"]
        self.mount_workdir: bool = task_descriptor["mount_workdir"]
        self.connect_to_network: bool = task_descriptor["connect_to_network"]
        self.extra_args: str = task_descriptor["extra_args"]
        self.image: str = task_descriptor["image"]
        self.command: str = task_descriptor["command"]
        self.enable_api: bool = task_descriptor["enable_api"]
        self.host_name: str = task_descriptor["host_name"]

        if self.host_name == "local":
            self.host = hosts.local
        else:
            try:
                self.host = hosts.remotes[self.host_name]
            except KeyError:
                raise TaskError(f"Host {self.host_name} not available.")

    # def run(self, hosts: Hosts, cmd_extra_args: str) -> None:
    #     host: Host = hosts.remotes[self.host_name]
    #     command = "docker run"
    #     if self.rm == True:
    #         command += " --rm"

    #     if self.mount_workdir == True:
    #         pass

    #     if host.container_engine.run_tasks_as_current_user:
    #         command += " -u $(id -u):$(id -g)"

    #     if host.container_engine.enable_docker_network and self.connect_to_network:
    #         command += f" --network {host.name}"

    #     command += f" --name {self.name} {self.extra_args} {self.image}"

    #     if self.command or cmd_extra_args:
    #         command += f" /bin/bash -c \"{self.command} {cmd_extra_args}\""

    #     if self.enable_api == True:
    #         host.container_engine.api_server.start()

    #     print(command)  