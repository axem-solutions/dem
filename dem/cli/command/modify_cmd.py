"""modify CLI command implementation."""
# dem/cli/command/modify_cmd

import copy, typer
from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal, DevEnv
from dem.cli.console import stderr
from dem.cli.tui.renderable.menu import ToolTypeMenu, ToolImageMenu, SelectMenu
from dem.core.tool_images import ToolImages
from dem.cli.tui.panel.tool_type_selector import ToolTypeSelectorPanel
from dem.cli.tui.panel.tool_image_selector import ToolImageSelectorPanel

tool_image_statuses = {
    ToolImages.LOCAL_ONLY: "local",
    ToolImages.REGISTRY_ONLY: "registry",
    ToolImages.LOCAL_AND_REGISTRY: "local and registry"
}

def get_tool_image_list(tool_images: ToolImages) -> list[list[str]]:
    return [[name, tool_image_statuses[status]] for name, status in tool_images.elements.items()]

def handle_tool_type_selector_panel(tool_type_selector_panel: ToolTypeSelectorPanel, 
                                    dev_env_name: str) -> list[str]:
    tool_type_selector_panel.tool_type_menu.set_title("What kind of tools would you like to include in [cyan]" + dev_env_name + "[/]?")

    tool_type_selector_panel.wait_for_user()

    if "cancel" in tool_type_selector_panel.cancel_next_menu.get_selection():
        raise(typer.Abort())

    tool_type_selector_panel.cancel_next_menu.is_selected = False

    return tool_type_selector_panel.tool_type_menu.get_selected_tool_types()

def handle_tool_iamge_selector_panel(tool_image_selector_panel: ToolImageSelectorPanel, 
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

def get_modifications_from_user(dev_env: DevEnvLocal, tool_image_list: list[list[str]]) -> None:
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
            selected_tool_image = handle_tool_iamge_selector_panel(current_panel, selected_tool_types[tool_index])

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

            if isinstance(current_panel, ToolImageSelectorPanel):
                current_panel.dev_env_status.set_tool_image(tool_selection)

    dev_env.tools = []
    for tool_type, tool_image in tool_selection.items():
        tool_descriptor = {
            "type": tool_type,
            "image_name": tool_image.split(":")[0],
            "image_version": tool_image.split(":")[1]
        }
        dev_env.tools.append(tool_descriptor)

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