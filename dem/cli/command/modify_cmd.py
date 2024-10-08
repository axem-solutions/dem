"""modify CLI command implementation."""
# dem/cli/command/modify_cmd

import copy, typer
from dem.core.dev_env import DevEnv, DevEnv
from dem.core.tool_images import ToolImage
from dem.core.platform import Platform
from dem.core.exceptions import PlatformError
from dem.cli.console import stderr, stdout
from dem.cli.tui.renderable.menu import SelectMenu
from dem.cli.tui.window.dev_env_settings_window import DevEnvSettingsWindow
from dem.cli.tui.printable_tool_image import PrintableToolImage, convert_to_printable_tool_images

def get_confirm_from_user() -> str:
    """ Get the confirmation from the user.
        
        Returns:
            the confirmation option
    """
    confirm_menu_items = ["confirm", "save as", "cancel"]
    select_menu = SelectMenu(confirm_menu_items)
    select_menu.set_title("Are you sure to overwrite the Development Environment?")
    select_menu.wait_for_user()
    return select_menu.get_selected()

def handle_user_confirm(confirmation: str, dev_env_local: DevEnv, platform: Platform) -> None:
    """ Handle the user confirmation.
    
        Args:
            confirmation -- the confirmation option
            dev_env_local -- the local Development Environment
            platform -- the platform

        Exceptions:
            typer.Abort -- when the user tries to save as the Dev Env with a taken name or cancels 
                           the operation
    """
    if confirmation == "cancel":
        raise typer.Abort()

    if confirmation == "save as":
        new_dev_env = copy.deepcopy(dev_env_local)
        new_dev_env.name = typer.prompt("Name of the new Development Environment")
        
        check_for_new_dev_env = platform.get_dev_env_by_name(new_dev_env.name)

        if check_for_new_dev_env is None:
            platform.local_dev_envs.append(new_dev_env)
        else:
            stderr.print("[red]The Development Environment already exist.")
            raise typer.Abort()

    platform.flush_dev_env_properties()

def get_already_selected_tool_images(dev_env: DevEnv) -> set[str]:
    """ Get the already selected Tool Images.
    
        Args:
            dev_env -- the Development Environment
            
        Returns:
            the already selected Tool Images
    """
    already_selected_tool_images = []
    for tool in dev_env.tool_image_descriptors:
        already_selected_tool_images.append(tool["image_name"] + ":" + tool["image_version"])

    return already_selected_tool_images

def remove_missing_tool_images(all_tool_images: dict[str, ToolImage], 
                               already_selected_tool_images: list[str]) -> None:
    """ Remove the missing Tool Images from the Development Environment.
        
            Args:
                all_tool_images -- all available Tool Images
                already_selected_tool_images -- the already selected Tool Images
            
            Exceptions:
                typer.Abort -- if the user doesn't want the removal of the missing Tool Images
    """
    tool_images_are_missing = False

    for already_selected_tool_image in already_selected_tool_images:
        try:
            all_tool_images[already_selected_tool_image]
        except KeyError:
            stderr.print(f"[red]The {already_selected_tool_image} is not available anymore.[/]")
            already_selected_tool_images.remove(already_selected_tool_image)
            tool_images_are_missing = True
    
    if tool_images_are_missing:
        typer.confirm("By continuing, the missing tool images will be removed from the Development Environment.", 
                    abort=True)

def open_dev_env_settings_panel(already_selected_tool_images: list[str], 
                                printable_tool_images: list[PrintableToolImage]) -> list[str]:
    """ Open the Development Environment settings panel.
    
        Args:
            already_selected_tool_images -- the already selected Tool Images
            printable_tool_images -- the printable Tool Images
        
        Returns:
            the selected Tool Images

        Exceptions:
            typer.Abort -- if the user cancels the operation
    """
    dev_env_settings_panel = DevEnvSettingsWindow(printable_tool_images, already_selected_tool_images)
    dev_env_settings_panel.wait_for_user()

    if "cancel" in dev_env_settings_panel.cancel_save_menu.get_selection():
        raise typer.Abort()

    return dev_env_settings_panel.tool_image_menu.get_selected_tool_images()

def update_dev_env(dev_env: DevEnv, selected_tool_images: list[str]) -> None:
    """ Update the Development Environment.
    
        Args:
            dev_env -- the Development Environment
            selected_tool_images -- the selected Tool Images
    """
    dev_env.tool_image_descriptors = []

    for tool_image in selected_tool_images:
        if "/" in tool_image:
            registry, image = tool_image.split("/")
            image_name = registry + '/' + image.split(":")[0]
        else:
            image = tool_image
            image_name = image.split(":")[0]

        dev_env.tool_image_descriptors.append({
            "image_name": image_name,
            "image_version": image.split(":")[1]
        })

def modify_with_tui(platform: Platform, dev_env: DevEnv) -> None:
    """ Modify the Dev Env with the TUI.
    
        Args:
            platform -- the platform
            dev_env -- the Development Environment
            
        Exceptions:
            typer.Abort -- if the user cancels the operation
    """
    already_selected_tool_images = get_already_selected_tool_images(dev_env)
    remove_missing_tool_images(platform.tool_images.all_tool_images, already_selected_tool_images)
    printable_tool_images = convert_to_printable_tool_images(platform.tool_images.all_tool_images)
    selected_tool_images = open_dev_env_settings_panel(already_selected_tool_images, 
                                                       printable_tool_images)
    update_dev_env(dev_env, selected_tool_images)
    confirmation = get_confirm_from_user()
    handle_user_confirm(confirmation, dev_env, platform)

def execute(platform: Platform, dev_env_name: str) -> None:
    """ Modify the Development Environment.
    
        Args:
            platform -- the platform
            dev_env_name -- the name of the Development Environment
            
        Exceptions:
            typer.Abort -- if the user cancels the operation
    """

    platform.get_tool_image_info_from_registries = True
    platform.assign_tool_image_instances_to_all_dev_envs()

    dev_env = platform.get_dev_env_by_name(dev_env_name)

    if dev_env is None:
        stderr.print("[red]The Development Environment doesn't exist.")
        return
    elif dev_env.is_installed is True:
        stdout.print("[yellow]The Development Environment is installed, so it can't be modified.[/]")
        typer.confirm("Do you want to uninstall it first?", abort=True)
        try:
            for status in platform.uninstall_dev_env(dev_env):
                stdout.print(status)
        except PlatformError as e:
            stderr.print(f"[red]{str(e)}[/]")
            return

    modify_with_tui(platform, dev_env)
    stdout.print("[green]The Development Environment has been modified successfully![/]")