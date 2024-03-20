"""create CLI command implementation."""
# dem/cli/command/create_cmd.py

import typer
from dem.core.dev_env import DevEnv, DevEnv
from dem.core.tool_images import ToolImages
from dem.core.platform import Platform
from dem.core.exceptions import PlatformError
from dem.cli.console import stdout, stderr
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
    tool_image_selector_panel.tool_image_menu.set_title("Select tool image for: [yellow]" + tool_type + "[/]")
    tool_image_selector_panel.wait_for_user()

    if tool_image_selector_panel.back_menu.is_selected is True:
        # Reset the back menu selection
        tool_image_selector_panel.back_menu.is_selected = False
        return None
    else:
        tool_image_selector_panel.tool_image_menu.is_selected = False
        return tool_image_selector_panel.tool_image_menu.get_selected_tool_image()

def get_dev_env_descriptor_from_user(dev_env_name: str, tool_image_list: list[list[str]]) -> dict:
    current_panel = ToolTypeSelectorPanel(list(DevEnv.supported_tool_types))
    panel_list = [current_panel]

    tool_index = 0
    panel_index = 0
    tool_selection = {}
    while current_panel is not None:
        if isinstance(current_panel, ToolTypeSelectorPanel):
            selected_tool_types = handle_tool_type_selector_panel(current_panel, dev_env_name)

            # Remove the not selected tool type from the tool_selection.
            for tool_type in list(tool_selection.keys()):
                if tool_type not in selected_tool_types:
                    del tool_selection[tool_type]

            if len(panel_list) > 1:
                current_panel = panel_list[1]
                current_panel.dev_env_status.reset_table(selected_tool_types)
            else:
                current_panel = ToolImageSelectorPanel(tool_image_list, selected_tool_types)
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

    dev_env_descriptor = {
        "name": dev_env_name,
        "tools": []
    }

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
        dev_env_descriptor["tools"].append(tool_descriptor)

    return dev_env_descriptor

def create_new_dev_env(platform: Platform, new_dev_env_descriptor: dict) -> None:
    """ Create a new Development Environment.
        
        Args:
            platform -- the platform
            new_dev_env_descriptor -- the descriptor of the new Development Environment
    """
    new_dev_env = DevEnv(new_dev_env_descriptor)
    platform.local_dev_envs.append(new_dev_env)

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
                platform.uninstall_dev_env(dev_env_original)
            except PlatformError as e:
                stderr.print(f"[red]{str(e)}[/]")
                typer.Abort()

    tool_image_list = get_tool_image_list(platform.tool_images)
    new_dev_env_descriptor = get_dev_env_descriptor_from_user(dev_env_name, tool_image_list)
    
    if dev_env_original is not None:
        dev_env_original.tools = new_dev_env_descriptor["tools"]
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
    create_dev_env(platform, dev_env_name)
    platform.flush_descriptors()
    stdout.print(f"The [green]{dev_env_name}[/] Development Environment has been created!")
    stdout.print("Run [italic]dem install[/] to install it.")