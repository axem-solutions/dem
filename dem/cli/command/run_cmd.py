"""run CLI command implementation."""
# dem/cli/command/run_cmd.py

from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal
from dem.cli.console import stdout, stderr
import typer

def handle_invalid_dev_env(dev_env_name: str) -> None:
    """
    Report an error that the input Dev Env name is invalid.
    
    Args:
        dev_env_name -- invalid Dev Env name
    """
    stderr.print("[red]Error: Unknown Development Environment: " + dev_env_name + "[/]")
    raise(typer.Abort)

def handle_invalid_tool_type(tool_type: str, dev_env_name: str) -> None:
    """
    Report an error that the input tool type is invalid. 
    
    Args: 
        tool_type -- invalid tool type
        dev_env_name -- name of the Dev Env in which the tool type is not present
    """
    stderr.print("[red]Error: There is no [b]" + tool_type + "[/b] in [b]" + dev_env_name + "[/]")
    raise(typer.Abort)

def handle_missing_tool_images(missing_tool_images: set[str], dev_env_local: DevEnvLocal,
                               dev_env_local_setup: DevEnvLocalSetup) -> None:
    """
    Report an error to the user that some images are not available. Ask them if the DEM should try
    to fix the Dev Env: abort if no, pull the missing tool images if yes.
    
    Args:
        missing_tool_images -- the missing tool images
        dev_env_local -- local Dev Env
        dev_env_local_setup -- local setup
        """
    stderr.print("[red]Error: The following tool images are not available locally:[/]")
    for missing_tool_image in missing_tool_images:
        stderr.print("[red]" + missing_tool_image + "[/]")
    typer.confirm("Should DEM try to fix the faulty Development Environment?", abort=True)

    dev_env_local.check_image_availability(dev_env_local_setup.tool_images, 
                                        update_tool_images=True)
    dev_env_local_setup.pull_images(dev_env_local.tools)
    stdout.print("[green]DEM fixed the " + dev_env_local.name + "![/]")

def execute(dev_env_name: str, tool_type: str, workspace_path: str, command: str, privileged: bool) -> None:
    """
    Execute the run command. 

    Args:
        dev_env_name -- name of the Development Environment
        tool_type -- tool type to run
        workspace_path -- workspace path
        command -- command to be passed to the assigned tool image
        priviliged -- give extended priviliges to the container
    """
    dev_env_local_setup = DevEnvLocalSetup()
    dev_env_local = dev_env_local_setup.get_dev_env_by_name(dev_env_name)

    if dev_env_local is None:
        handle_invalid_dev_env(dev_env_name)
    else:
        # Update the tool images manually.
        DevEnvLocalSetup.update_tool_images_on_instantiation = False
        # Only the local images are needed.
        dev_env_local_setup.tool_images.local.update()

        tool_image_to_run = ""
        missing_tool_images = set()
        for tool in dev_env_local.tools:
            tool_image = tool["image_name"] + ":" + tool["image_version"]

            # Check if the required tool image exists locally.
            if tool_image not in dev_env_local_setup.tool_images.local.elements:
                missing_tool_images.add(tool_image)

            if tool["type"] == tool_type:
                tool_image_to_run = tool_image

        if tool_image_to_run == "":
            handle_invalid_tool_type(tool_type, dev_env_name)

        if missing_tool_images:
            handle_missing_tool_images(missing_tool_images, dev_env_local, dev_env_local_setup)

        dev_env_local_setup.run_container(tool_image_to_run, workspace_path, command, privileged)