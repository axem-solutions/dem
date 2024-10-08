"""This module represents a Development Environment."""
# dem/core/dev_env.py

from dem.core.tool_images import ToolImage, ToolImages
from enum import Enum
import json, os

class DevEnv():
    """ A Development Environment. """

    def __init__(self, descriptor: dict | None = None, descriptor_path: str | None = None) -> None:
        """ Init the DevEnv class. 
        
            A new instance can be created:
            - from a Dev Env descriptor
            - from a descriptor avaialable at the given path.

            Only one of the arguments can be used at a time.
        
            Args:
                descriptor -- the description of the Development Environment from the dev_env.json 
                              file
                descriptor_path -- the path of the descriptor file

            Exceptions:
                ValueError -- if more than one of the arguments is not None
        """

        # Only one of the arguments can be not None
        if sum(arg is not None for arg in [descriptor, descriptor_path]) > 1:
            raise ValueError("Only one of the arguments can be not None.")

        if descriptor_path:
            if not os.path.exists(descriptor_path):
                raise FileNotFoundError("dev_env_descriptor.json doesn't exist.")
            with open(descriptor_path, "r") as file:
                descriptor = json.load(file)

        self.name: str = descriptor["name"]
        self.tool_image_descriptors: list[dict[str, str]] = descriptor["tools"]
        self.tool_images: list[ToolImage] = []
        self.tasks: dict[str, str] = descriptor.get("tasks", {})
        if "True" == descriptor.get("installed", "False"):
            self.is_installed = True
        else:
            self.is_installed = False

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
        self.tasks[task_name] = command

    def del_task(self, task_name: str) -> None:
        """ Delete a task from the Development Environment.

            Args:
                task_name -- the task name

            Exceptions:
                KeyError -- if the task doesn't exist
        """
        if task_name in self.tasks:
            del self.tasks[task_name]
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

    def get_deserialized(self, omit_is_installed: bool = False) -> dict[str, str]:
        """ Create the deserialized json. 
        
            Return the Dev Env as a dict.
        """
        dev_env_json_deserialized: dict = {
            "name": self.name,
            "tools": self.tool_image_descriptors,
            "tasks": self.tasks
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