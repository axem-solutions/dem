"""This module represents a Development Environment."""
# dem/core/dev_env.py

from dem.core.tool_images import ToolImage, ToolImages
import json
import os

class DevEnv:
    """ A Development Environment. """

    def __init__(self, descriptor: dict) -> None:
        """ Initialize the DevEnv class.

        Args:
            descriptor -- The description of the Development Environment from the dev_env.json file.
        """
        self.name = descriptor["name"]
        self.tool_image_descriptors = descriptor["tools"]
        self.tool_images = []
        self.custom_tasks = descriptor.get("custom_tasks", [])
        self.docker_run_tasks = descriptor.get("docker_run_tasks", [])
        self.run_tasks_as_current_user = descriptor.get("run_tasks_as_current_user", False)
        self.enable_docker_network = descriptor.get("enable_docker_network", False)
        self.is_installed = descriptor.get("installed", "False") == "True"

    @classmethod
    def from_descriptor_path(cls, descriptor_path: str) -> "DevEnv":
        """ Create a DevEnv instance from a descriptor path.

        Args:
            descriptor_path -- The path of the descriptor file.

        Returns:
            DevEnv -- An instance of the DevEnv class.

        Raises:
            FileNotFoundError -- If the descriptor file does not exist.
        """
        if not os.path.exists(descriptor_path):
            raise FileNotFoundError(f"{descriptor_path} doesn't exist.")
        with open(descriptor_path, "r") as file:
            descriptor = json.load(file)
        return cls(descriptor)

    def assign_tool_image_instances(self, tool_images: ToolImages) -> None:
        """ Assign the Tool Images to the Development Environment.
        
            After creating a DevEnv instance, the Tool Images are not yet assigned to it. This 
            method must be called if the Tool Images are needed.
            
            Args:
                tool_images -- the Tool Images to assign
                
                Exceptions:
                    ToolImageError -- if the Tool Image name is invalid
        """
        self.tool_images = []
        for tool_descriptor in self.tool_image_descriptors:
            tool_image_name = tool_descriptor["image_name"] + ':' + tool_descriptor["image_version"]
            tool_image = tool_images.all_tool_images.get(tool_image_name, ToolImage(tool_image_name))
            self.tool_images.append(tool_image)

    def add_task(self, task_name: str, command: str) -> None:
        """ Add a task to the Development Environment.

            If the task already exists, it will be overwritten.
        
            Args:
                task_name -- the task name
                command -- the command
        """
        self.custom_tasks[task_name] = command

    def del_task(self, task_name: str) -> None:
        """ Delete a task from the Development Environment.

            Args:
                task_name -- the task name

            Exceptions:
                KeyError -- if the task doesn't exist
        """
        if task_name in self.custom_tasks:
            del self.custom_tasks[task_name]
        else:
            raise KeyError(f"Task [bold]{task_name}[/] not found.")

    def is_installation_correct(self) -> bool:
        """ Check if the installation is correct.

            Return True if the Dev Env is in installed state and all the Tool Images are available, 
            otherwise False.
        """
        if self.is_installed:
            for tool_image in self.tool_images:
                if tool_image.availability == ToolImage.NOT_AVAILABLE:
                    break
            else:
                return True
        return False

    def get_deserialized(self, omit_is_installed: bool = False) -> dict:
        """ Create the deserialized json. 
        
            Return the Dev Env as a dict.
        """
        dev_env_json_deserialized: dict = {
            "name": self.name,
            "tools": self.tool_image_descriptors,
            "custom_tasks": self.custom_tasks,
            "docker_run_tasks": self.docker_run_tasks,
            "run_tasks_as_current_user": self.run_tasks_as_current_user,
            "enable_docker_network": self.enable_docker_network
        }
        
        if omit_is_installed is False:
            if self.is_installed:
                dev_env_json_deserialized["installed"] = "True"
            else:
                dev_env_json_deserialized["installed"] = "False"

        return dev_env_json_deserialized

    def export(self, path: str) -> None:
        """ Export the Dev Env to a file.
        
            Args:
                path -- the path of the file to export the Dev Env to
        """
        with open(path, "w") as file:
            json.dump(self.get_deserialized(True), file, indent=4)

def convert_to_tool_descriptor(tool_images: list[str]) -> list[dict]:
    """ Convert the tool images to tool descriptors.
    
        Args:
            tool_images -- the tool images
            
        Returns:
            the tool descriptors
    """
    tool_descriptors = []

    for tool_image in tool_images:
        if "/" in tool_image:
            registry, image = tool_image.split("/")
            image_name = registry + '/' + image.split(":")[0]
        else:
            image = tool_image
            image_name = image.split(":")[0]

        try:
            image_tag = image.split(":")[1]
        except IndexError:
            image_tag = "latest"

        tool_descriptor = {
            "image_name": image_name,
            "image_version": image_tag
        }

        tool_descriptors.append(tool_descriptor)

    return tool_descriptors
