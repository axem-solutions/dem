"""modify CLI command implementation."""
# dem/cli/command/modify_cmd

import dem.core.data_management as data_management
import dem.core.container_engine as container_engine
import dem.core.registry as registry
from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal, DevEnv
from dem.cli.console import stderr
from dem.cli.menu import ToolTypeMenu, ToolImageMenu, SelectMenu
from dem.core.tool_images import ToolImages

tool_image_statuses = {
    ToolImages.LOCAL_ONLY: "local",
    ToolImages.REGISTRY_ONLY: "registry",
    ToolImages.LOCAL_AND_REGISTRY: "local and registry"
}

def get_tool_images() -> list[list[str]]:
    tool_images = ToolImages()
    return [[name, tool_image_statuses[status]] for name, status in tool_images.elements.items()]

def get_modifications_from_user(dev_env: DevEnvLocal) -> None:
    selected_tool_types = []
    # Get tools that are already selected for this Dev Env.
    for tool in dev_env.tools:
        selected_tool_types.append(tool["type"])

    tool_type_menu = ToolTypeMenu(list(DevEnv.supported_tool_types))
    tool_type_menu.preset_selection(selected_tool_types)
    tool_type_menu.wait_for_user()
    selected_tool_types = tool_type_menu.get_selected_tool_types()

    tool_image_menu = ToolImageMenu(get_tool_images())

    tools = []
    for tool_type in selected_tool_types:
        menu_title = "Select tool image for type " + tool_type
        for original_tool_type in dev_env.tools:
            if original_tool_type["type"] == tool_type:
                menu_title += " -- not modified"
                tool_image = original_tool_type["image_name"] + ":" + original_tool_type["image_version"]
                tool_image_menu.set_cursor(tool_image)
                break
        else:
            menu_title = menu_title + " -- [yellow]new![/]"
        tool_image_menu.set_title(menu_title)
        tool_image_menu.wait_for_user()
        selected_tool_image = tool_image_menu.get_selected_tool_image()
        tool_descriptor = {
            "type": tool_type,
            "image_name": selected_tool_image[0],
            "image_version": selected_tool_image[1]
        }
        tools.append(tool_descriptor)
    dev_env.tools = tools

def get_confirm_from_user() -> None:
    confirm_menu_selection = ["confirm", "save as", "cancel"]
    select_menu = SelectMenu(confirm_menu_selection)
    select_menu.set_title("Are you sure to overwrite the Development Environment?")
    select_menu.wait_for_user()

def execute(dev_env_name: str) -> None:
    deserialized_local_dev_nev = data_management.read_deserialized_dev_env_json()
    dev_env_local_setup = DevEnvLocalSetup(deserialized_local_dev_nev)
    dev_env = dev_env_local_setup.get_dev_env_by_name(dev_env_name)
    if dev_env is None:
        stderr.print("[red]The Development Environment doesn't exist.")
    else:
        get_modifications_from_user(dev_env)
        get_confirm_from_user()
        deserialized_local_dev_nev = dev_env_local_setup.get_deserialized()
        data_management.write_deserialized_dev_env_json(deserialized_local_dev_nev)