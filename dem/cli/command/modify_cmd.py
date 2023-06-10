"""modify CLI command implementation."""
# dem/cli/command/modify_cmd

import copy, typer
from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal, DevEnv
from dem.cli.console import stderr
from dem.cli.tui.renderable.menu import ToolTypeMenu, ToolImageMenu, SelectMenu
from dem.core.tool_images import ToolImages

tool_image_statuses = {
    ToolImages.LOCAL_ONLY: "local",
    ToolImages.REGISTRY_ONLY: "registry",
    ToolImages.LOCAL_AND_REGISTRY: "local and registry"
}

def get_tool_image_list(tool_images: ToolImages) -> list[list[str]]:
    return [[name, tool_image_statuses[status]] for name, status in tool_images.elements.items()]

def get_modifications_from_user(dev_env: DevEnvLocal, tool_image_list: list[list[str]]) -> None:
    selected_tool_types = []
    # Get tools that are already selected for this Dev Env.
    for tool in dev_env.tools:
        selected_tool_types.append(tool["type"])

    tool_type_menu = ToolTypeMenu(list(DevEnv.supported_tool_types))
    tool_type_menu.preset_selection(selected_tool_types)
    tool_type_menu.wait_for_user()
    selected_tool_types = tool_type_menu.get_selected_tool_types()

    tool_image_menu = ToolImageMenu(tool_image_list)

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

def get_confirm_from_user() -> str:
    confirm_menu_items = ["confirm", "save as", "cancel"]
    select_menu = SelectMenu(confirm_menu_items)
    select_menu.set_title("Are you sure to overwrite the Development Environment?")
    select_menu.wait_for_user()
    return select_menu.get_selected()

def handle_user_confirm(confirmation: str, dev_env_local: DevEnvLocal,
                        dev_env_local_setup: DevEnvLocalSetup) -> None:
    if confirmation == "cancel":
        raise(typer.Abort())

    if confirmation == "save as":
        new_dev_env = copy.deepcopy(dev_env_local)
        new_dev_env.name = typer.prompt("Name of the new Development Environment")
        dev_env_local_setup.dev_envs.append(new_dev_env)

    # Update the json file if the user confirms or saves as a new Dev Env.
    dev_env_local_setup.update_json()

def execute(dev_env_name: str) -> None:
    dev_env_local_setup = DevEnvLocalSetup()
    dev_env_local = dev_env_local_setup.get_dev_env_by_name(dev_env_name)

    if dev_env_local is None:
        stderr.print("[red]The Development Environment doesn't exist.")
    else:
        tool_image_list = get_tool_image_list(dev_env_local_setup.tool_images)
        get_modifications_from_user(dev_env_local, tool_image_list)
        confirmation = get_confirm_from_user()
        handle_user_confirm(confirmation, dev_env_local, dev_env_local_setup)