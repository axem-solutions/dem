"""modify CLI command implementation."""
# dem/cli/command/modify_cmd

import copy, typer
from dem.core.dev_env import DevEnv, convert_to_tool_descriptor
from dem.core.tool_images import ToolImage
from dem.core.platform import Platform
from dem.core.exceptions import PlatformError
from dem.cli.console import stderr, stdout
from dem.cli.tui.window.dev_env_settings_window import DevEnvSettingsWindow
from dem.cli.tui.printable_tool_image import PrintableToolImage, convert_to_printable_tool_images

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
    missing_tool_images_to_remove: list[str] = []

    for already_selected_tool_image in already_selected_tool_images:
        try:
            all_tool_images[already_selected_tool_image]
        except KeyError:
            stderr.print(f"[red]The {already_selected_tool_image} is not available anymore.[/]")
            missing_tool_images_to_remove.append(already_selected_tool_image)
    
    if missing_tool_images_to_remove:
        typer.confirm("By continuing, the missing tool images will be removed from the Development Environment.", 
                    abort=True)

        for missing_tool_image in missing_tool_images_to_remove:
            already_selected_tool_images.remove(missing_tool_image)

def open_dev_env_settings_window(already_selected_tool_images: list[str], 
                                printable_tool_images: list[PrintableToolImage]) -> DevEnvSettingsWindow:
    """ Open the Development Environment settings panel.
    
        Args:
            already_selected_tool_images -- the already selected Tool Images
            printable_tool_images -- the printable Tool Images
        
        Returns:
            The closed Development Environment settings window.

        Exceptions:
            typer.Abort -- if the user cancels the operation
    """
    dev_env_settings_window = DevEnvSettingsWindow(printable_tool_images, already_selected_tool_images)
    dev_env_settings_window.run()

    if dev_env_settings_window.last_button_pressed is None or \
        dev_env_settings_window.last_button_pressed is dev_env_settings_window.cancel_button_id:
        raise typer.Abort()

    return dev_env_settings_window

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
    dev_env_settings_window = open_dev_env_settings_window(already_selected_tool_images, 
                                                       printable_tool_images)

    if dev_env_settings_window.last_button_pressed == dev_env_settings_window.cancel_button_id:
        raise typer.Abort()
    elif dev_env_settings_window.last_button_pressed == dev_env_settings_window.confirm_screen_save_as_button_id:
        new_dev_env = copy.deepcopy(dev_env)
        new_dev_env.tool_image_descriptors  = convert_to_tool_descriptor(dev_env_settings_window.selected_tool_images)
        new_dev_env.name = typer.prompt("Name of the new Development Environment")
        
        check_for_new_dev_env = platform.get_dev_env_by_name(new_dev_env.name)

        if check_for_new_dev_env is None:
            platform.local_dev_envs.append(new_dev_env)
        else:
            stderr.print("[red]The Development Environment already exist.")
            raise typer.Abort()
    elif dev_env_settings_window.last_button_pressed == dev_env_settings_window.confirm_screen_confirm_button_id:
        dev_env.tool_image_descriptors = convert_to_tool_descriptor(dev_env_settings_window.selected_tool_images)

    platform.flush_dev_env_properties()

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