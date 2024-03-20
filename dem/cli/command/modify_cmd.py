"""modify CLI command implementation."""
# dem/cli/command/modify_cmd

import copy, typer
from dem.core.dev_env import DevEnv, DevEnv
from dem.core.tool_images import ToolImages
from dem.core.platform import Platform
from dem.core.exceptions import PlatformError
from dem.cli.console import stderr, stdout
from dem.cli.tui.renderable.menu import SelectMenu
from dem.cli.tui.panel.tool_type_selector import ToolTypeSelectorPanel
from dem.cli.tui.panel.tool_image_selector import ToolImageSelectorPanel

tool_image_statuses = {
    ToolImages.LOCAL_ONLY: "local",
    ToolImages.REGISTRY_ONLY: "registry",
    ToolImages.LOCAL_AND_REGISTRY: "local and registry"
}

def get_tool_image_list(tool_images: ToolImages) -> list[list[str]]:
    """
    Combine the registry and local tool images, and assign the availabilities. 
    
    Args:
        tool_images -- all the tool images
    """
    tool_image_list = []

    for tool_image in tool_images.registry.elements:
        if tool_image in tool_images.local.elements:
            tool_image_list.append([tool_image, tool_image_statuses[ToolImages.LOCAL_AND_REGISTRY]])
        else:
            tool_image_list.append([tool_image, tool_image_statuses[ToolImages.REGISTRY_ONLY]])

    for tool_image in tool_images.local.elements:
        if tool_image not in tool_images.registry.elements:
            tool_image_list.append([tool_image, tool_image_statuses[ToolImages.LOCAL_ONLY]])

    return tool_image_list

def handle_tool_type_selector_panel(tool_type_selector_panel: ToolTypeSelectorPanel, 
                                    dev_env_name: str) -> list[str]:
    tool_type_selector_panel.tool_type_menu.set_title("What kind of tools would you like to include in [cyan]" + dev_env_name + "[/]?")

    tool_type_selector_panel.wait_for_user()

    if "cancel" in tool_type_selector_panel.cancel_next_menu.get_selection():
        raise(typer.Abort())

    tool_type_selector_panel.cancel_next_menu.is_selected = False

    return tool_type_selector_panel.tool_type_menu.get_selected_tool_types()

def handle_tool_image_selector_panel(tool_image_selector_panel: ToolImageSelectorPanel, 
                                     tool_type:str) -> str | None:
    tool_image_selector_panel.tool_image_menu.set_title("Select tool image for type " + tool_type)
    tool_image_selector_panel.wait_for_user()

    if tool_image_selector_panel.back_menu.is_selected is True:
        # Reset the back menu selection
        tool_image_selector_panel.back_menu.is_selected = False
        return None
    else:
        tool_image_selector_panel.tool_image_menu.is_selected = False
        return tool_image_selector_panel.tool_image_menu.get_selected_tool_image()

def get_modifications_from_user(dev_env: DevEnv, tool_image_list: list[list[str]]) -> None:
    already_selected_tool_types = []
    tool_selection = {}
    for tool in dev_env.tools:
        already_selected_tool_types.append(tool["type"])
        tool_selection[tool["type"]] = tool["image_name"] + ":" + tool["image_version"]

    current_panel = ToolTypeSelectorPanel(list(DevEnv.supported_tool_types))
    current_panel.tool_type_menu.preset_selection(already_selected_tool_types)
    panel_list = [current_panel]

    tool_index = 0
    panel_index = 0
    while current_panel is not None:
        if isinstance(current_panel, ToolTypeSelectorPanel):
            selected_tool_types = handle_tool_type_selector_panel(current_panel, dev_env.name)

            # Remove the not selected tool type from the tool_selection.
            for tool_type in list(tool_selection.keys()):
                if tool_type not in selected_tool_types:
                    del tool_selection[tool_type]

            if len(panel_list) > 1:
                current_panel = panel_list[1]
                current_panel.dev_env_status.reset_table(selected_tool_types)
            else:
                current_panel = ToolImageSelectorPanel(tool_image_list, selected_tool_types)
                current_panel.dev_env_status.set_tool_image(tool_selection)
                panel_list.append(current_panel)

            tool_index = 0
            panel_index = 1
        else:
            selected_tool_image = handle_tool_image_selector_panel(current_panel, selected_tool_types[tool_index])

            if selected_tool_image is None:
                tool_selection[selected_tool_types[tool_index]] = "<not selected>"

                panel_index -= 1
                current_panel = panel_list[panel_index]
                
                if tool_index != 0:
                    tool_index -= 1
            else:
                tool_selection[selected_tool_types[tool_index]] = selected_tool_image

                tool_index += 1
                
                if tool_index == len(selected_tool_types):
                    break

                panel_index += 1
                if len(panel_list) > panel_index:
                    current_panel = panel_list[panel_index]
                else:
                    current_panel = ToolImageSelectorPanel(tool_image_list, selected_tool_types)
                    panel_list.append(current_panel)

                current_panel.dev_env_status.reset_table(selected_tool_types)

            if isinstance(current_panel, ToolImageSelectorPanel):
                current_panel.dev_env_status.set_tool_image(tool_selection)

    dev_env.tools = []
    for tool_type, tool_image in tool_selection.items():
        if "/" in tool_image:
            registry, image = tool_image.split("/")
            image_name = registry + '/' + image.split(":")[0]
        else:
            image = tool_image
            image_name = image.split(":")[0]
        tool_descriptor = {
            "type": tool_type,
            "image_name": image_name,
            "image_version": image.split(":")[1]
        }
        dev_env.tools.append(tool_descriptor)

def get_confirm_from_user() -> str:
    confirm_menu_items = ["confirm", "save as", "cancel"]
    select_menu = SelectMenu(confirm_menu_items)
    select_menu.set_title("Are you sure to overwrite the Development Environment?")
    select_menu.wait_for_user()
    return select_menu.get_selected()

def handle_user_confirm(confirmation: str, dev_env_local: DevEnv, platform: Platform) -> None:
    if confirmation == "cancel":
        raise(typer.Abort())

    if confirmation == "save as":
        new_dev_env = copy.deepcopy(dev_env_local)
        new_dev_env.name = typer.prompt("Name of the new Development Environment")
        
        check_for_new_dev_env = platform.get_dev_env_by_name(new_dev_env.name)

        if check_for_new_dev_env is None:            
            platform.local_dev_envs.append(new_dev_env)
        else:
            stderr.print("[red]The Development Environment already exist.")
            raise(typer.Abort())

    platform.flush_descriptors()

def modify_single_tool(platform: Platform, dev_env: DevEnv, tool_type: str, tool_image: str) -> None:
    if tool_type and tool_image:
        if tool_image not in platform.tool_images.local.elements:
            if tool_image in platform.tool_images.registry.elements:
                platform.container_engine.pull(tool_image)
            else:
                stderr.print(f"[red]Error: The {tool_image} is not an available image.[/]")
                return

        for tool in dev_env.tools:
            if tool["type"] == tool_type:
                tool["image_name"] = tool_image.split(":")[0]
                tool["image_version"] = tool_image.split(":")[1]
                break
        else:
            dev_env.tools.append({
                "type": tool_type,
                "image_name": tool_image.split(":")[0],
                "image_version": tool_image.split(":")[1]
            })

        platform.flush_descriptors()
    else:
        stderr.print("[red]Error: The tool type and the tool image must be set together.[/]")
        return

def open_modify_panel(platform: Platform, dev_env: DevEnv) -> None:
    tool_image_list: list[list[str]] = get_tool_image_list(platform.tool_images)
    get_modifications_from_user(dev_env, tool_image_list)
    confirmation = get_confirm_from_user()
    handle_user_confirm(confirmation, dev_env, platform)

def execute(platform: Platform, dev_env_name: str, tool_type: str, tool_image: str) -> None:
    dev_env = platform.get_dev_env_by_name(dev_env_name)

    if dev_env is None:
        stderr.print("[red]The Development Environment doesn't exist.")
        return
    elif dev_env.is_installed is True:
        stdout.print("[yellow]The Development Environment is installed, so it can't be modified.[/]")
        typer.confirm("Do you want to uninstall it first?", abort=True)
        try:
            platform.uninstall_dev_env(dev_env)
        except PlatformError as e:
            stderr.print(f"[red]{str(e)}[/]")
            return

    if (tool_type or tool_image):
        modify_single_tool(platform, dev_env, tool_type, tool_image)
    else:
        open_modify_panel(platform, dev_env)