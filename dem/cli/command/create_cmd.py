"""create CLI command implementation."""
# dem/cli/command/create_cmd.py

import typer
from dem.core.dev_env import DevEnv
from dem.core.tool_images import ToolImage
from dem.core.platform import Platform
from dem.core.exceptions import PlatformError
from dem.cli.console import stdout, stderr
from dem.cli.tui.window.dev_env_settings_window import DevEnvSettingsWindow
from dem.cli.tui.printable_tool_image import convert_to_printable_tool_images

def open_dev_env_settings_panel(all_tool_images: dict[str, ToolImage]) -> list[str]:
    """ Open the Development Environment settings panel.
        
        Args:
            all_tool_images -- the Tool Images

        Returns:
            the selected Tool Image names
    """
    dev_env_settings_panel = DevEnvSettingsWindow(convert_to_printable_tool_images(all_tool_images))
    dev_env_settings_panel.wait_for_user()

    if "cancel" in dev_env_settings_panel.cancel_save_menu.get_selection():
        raise typer.Abort()

    return dev_env_settings_panel.tool_image_menu.get_selected_tool_images()

def create_new_dev_env_descriptor(dev_env_name: str, selected_tool_images: list[str]) -> dict:
    """ Create a new Development Environment descriptor.
        
        Args:
            dev_env_name -- the name of the Development Environment
            selected_tool_images -- the selected Tool Images

        Returns:
            the descriptor of the new Development Environment
    """
    dev_env_descriptor = {
        "name": dev_env_name,
        "tools": []
    }

    for tool_image in selected_tool_images:
        if "/" in tool_image:
            registry, image = tool_image.split("/")
            image_name = registry + '/' + image.split(":")[0]
        else:
            image = tool_image
            image_name = image.split(":")[0]

        tool_descriptor = {
            "image_name": image_name,
            "image_version": image.split(":")[1]
        }
        dev_env_descriptor["tools"].append(tool_descriptor)

    return dev_env_descriptor

def create_new_dev_env(platform: Platform, new_dev_env_descriptor: dict) -> None:
    """ Create a new Development Environment.
        
        Args:
            platform -- the platform
            new_dev_env_descriptor -- the descriptor of the new Development Environment
    """
    dev_env = DevEnv(descriptor=new_dev_env_descriptor)
    dev_env.assign_tool_image_instances(platform.tool_images)
    platform.local_dev_envs.append(dev_env)

def create_dev_env(platform: Platform, dev_env_name: str) -> None:
    """ Create a new Development Environment or overwrite an existing one.
        
        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment

        Exceptions:
            Abort -- if the name of the Development Environment contains whitespace characters
    """
    if ' ' in dev_env_name:
        stderr.print("The name of the Development Environment cannot contain whitespace characters!")
        raise typer.Abort()

    dev_env_original = platform.get_dev_env_by_name(dev_env_name)
    if dev_env_original is not None:
        typer.confirm("The input name is already used by a Development Environment. Overwrite it?", 
                      abort=True)

        if dev_env_original.is_installed:
            typer.confirm("The Development Environment is installed, so it can't be overwritten. " + \
                          "Uninstall it first?", abort=True)
            try:
                for status in platform.uninstall_dev_env(dev_env_original):
                    stdout.print(status)
            except PlatformError as e:
                stderr.print(f"[red]{str(e)}[/]")
                raise typer.Abort()

    selected_tool_images = open_dev_env_settings_panel(platform.tool_images.all_tool_images)
    new_dev_env_descriptor = create_new_dev_env_descriptor(dev_env_name, selected_tool_images)
    
    if dev_env_original is not None:
        dev_env_original.tool_image_descriptors = new_dev_env_descriptor["tools"]
    else:
        create_new_dev_env(platform, new_dev_env_descriptor)

def execute(platform: Platform, dev_env_name: str) -> None:
    """ Create a new Development Environment.
        
        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment

        Exceptions:
            Abort -- if the name of the Development Environment contains whitespace characters
    """
    platform.get_tool_image_info_from_registries = True
    platform.assign_tool_image_instances_to_all_dev_envs()

    create_dev_env(platform, dev_env_name)
    platform.flush_dev_env_properties()
    stdout.print(f"The [green]{dev_env_name}[/] Development Environment has been created!")
    stdout.print("Run [italic]dem install[/] to install it.")