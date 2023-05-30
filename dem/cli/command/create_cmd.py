"""create CLI command implementation."""
# dem/cli/command/create_cmd.py

import typer
from dem.core.dev_env_setup import DevEnv, DevEnvLocal, DevEnvLocalSetup
from dem.core.tool_images import ToolImages
from dem.cli.menu import ToolTypeMenu, ToolImageMenu
from dem.cli.console import stdout, stderr

tool_image_statuses = {
    ToolImages.LOCAL_ONLY: "local",
    ToolImages.REGISTRY_ONLY: "registry",
    ToolImages.LOCAL_AND_REGISTRY: "local and registry"
}

def get_tool_image_list(tool_images: ToolImages) -> list[list[str]]:
    return [[name, tool_image_statuses[status]] for name, status in tool_images.elements.items()]

def get_dev_env_descriptor_from_user(dev_env_name: str, tool_image_list: list[list[str]]) -> dict:
    tool_type_menu = ToolTypeMenu(list(DevEnv.supported_tool_types))
    # Wait until the user finishes the tool type selection.
    tool_type_menu.wait_for_user()
    selected_tool_types = tool_type_menu.get_selected_tool_types()

    tool_image_menu = ToolImageMenu(tool_image_list)
    dev_env_descriptor = {
        "name": dev_env_name,
        "tools": []
    }
    for tool_type in selected_tool_types:
        tool_image_menu.set_title("Select tool image for type " + tool_type)
        tool_image_menu.wait_for_user()
        selected_tool_image = tool_image_menu.get_selected_tool_image()
        tool_descriptor = {
            "type": tool_type,
            "image_name": selected_tool_image[0],
            "image_version": selected_tool_image[1]
        }
        dev_env_descriptor["tools"].append(tool_descriptor)
    return dev_env_descriptor

def overwrite_existing_dev_env(original_dev_env: DevEnvLocal, new_dev_env_descriptor: dict) -> None:
    original_dev_env.tools = new_dev_env_descriptor["tools"]

def create_new_dev_env(dev_env_local_setup: DevEnvLocalSetup, new_dev_env_descriptor: dict) -> DevEnvLocal:
    new_dev_env = DevEnvLocal(new_dev_env_descriptor)
    dev_env_local_setup.dev_envs.append(new_dev_env)

    return new_dev_env

def create_dev_env(dev_env_local_setup: DevEnvLocalSetup, dev_env_name: str) -> DevEnvLocal:
    dev_env_original = dev_env_local_setup.get_dev_env_by_name(dev_env_name)
    if dev_env_original is not None:
        typer.confirm("The input name is already used by a Development Environment. Overwrite it?", 
                      abort=True)

    tool_image_list = get_tool_image_list(dev_env_local_setup.tool_images)
    new_dev_env_descriptor = get_dev_env_descriptor_from_user(dev_env_name, tool_image_list)
    
    if dev_env_original is not None:
        overwrite_existing_dev_env(dev_env_original, new_dev_env_descriptor)
        new_dev_env = dev_env_original
    else:
        new_dev_env = create_new_dev_env(dev_env_local_setup, new_dev_env_descriptor)

    new_dev_env.check_image_availability(dev_env_local_setup.tool_images)
    dev_env_local_setup.pull_images(new_dev_env.tools)

    return new_dev_env

def execute(dev_env_name: str) -> None:
    dev_env_local_setup = DevEnvLocalSetup()
    dev_env = create_dev_env(dev_env_local_setup, dev_env_name)

    # Validate the Dev Env creation
    image_statuses = dev_env.check_image_availability(dev_env_local_setup.tool_images, 
                                                      update_tool_images=True)

    if (ToolImages.NOT_AVAILABLE in image_statuses) or (ToolImages.REGISTRY_ONLY in image_statuses):
        stderr.print("The installation failed.")
    else:
        stdout.print("The [yellow]" + dev_env.name + "[/] Development Environment is ready!")
        dev_env_local_setup.update_json()