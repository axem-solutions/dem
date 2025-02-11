""" This module contains the different task types. """
# dem/core/task.py

from dem.core.hosts import Hosts, Host
from dem.core.exceptions import TaskError
import os

class Task():
    """ A Task. """
    def __init__(self, task_descriptor: dict) -> None:
        """ Initialize the Task class.
        
            Args:
                task_descriptor -- The description of the task.
        """
        self.descriptor: dict = task_descriptor
        self.name: str = task_descriptor["name"]
        self.host_name: str = task_descriptor["host_name"]

class DockerTask(Task):
    """ A Docker Task. """
    def __init__(self, task_descriptor: dict, hosts: Hosts) -> None:
        """ Initialize the DockerTask class.
        
            Args:
                task_descriptor -- The description of the task.
                hosts -- The available hosts.
        """
        super().__init__(task_descriptor)
        self.rm: bool = task_descriptor["rm"]
        self.mount_workdir: bool = task_descriptor["mount_workdir"]
        self.connect_to_network: bool = task_descriptor["connect_to_network"]
        self.extra_args: str = task_descriptor["extra_args"]
        self.image: str = task_descriptor["image"]
        self.command: str = f"/bin/bash -c \"{task_descriptor['command']}\""
        self.enable_api: bool = task_descriptor["enable_api"]
        self.network: str | None = task_descriptor["network"]
        self.run_as_current_user: bool = task_descriptor["run_as_current_user"]

        if self.host_name == "local":
            self.host: Host = hosts.local
        else:
            try:
                self.host: Host = hosts.remotes[self.host_name]
            except KeyError:
                raise TaskError(f"Host {self.host_name} not available.")

    def run(self) -> None:
        """ Run the task. """
        if self.run_as_current_user:
            user: str = f"{os.getuid()}:{os.getgid()}"
        else:
            user: None = None

        self.host.container_engine.run(self.image, self.command, remove=self.rm, 
                                       network=self.network, name=self.name, user=user)