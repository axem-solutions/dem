"""delete CLI command implementation."""
# dem/cli/command/delete_cmd.py

from dem.core.dev_env import DevEnv
from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stderr, stdout
import typer
import docker.errors

def try_to_delete_tool_image(tool_image: str, dev_env_local_setup: DevEnvLocalSetup) -> None:
    stdout.print("\nThe tool image [bold]" + tool_image + "[/bold] is not required by any Development Environment anymore.")
    if typer.confirm("Would you like to remove it?"):
        try:
            dev_env_local_setup.container_engine.remove(tool_image)
        except docker.errors.ImageNotFound:
            stdout.print("[yellow]" + tool_image + " doesn't exist. Unable to remove it.[/]\n")
        except docker.errors.APIError:
            stderr.print("[red]Error: " + tool_image + " is used by a container. Unable to remove it.[/]\n")
        else:
            stdout.print("[green]Successfully removed![/]\n")

def remove_unused_tool_images(deleted_dev_env: DevEnv, dev_env_local_setup: DevEnvLocalSetup) -> None:
    all_required_tool_images = set()
    for dev_env in dev_env_local_setup.local_dev_envs:
        for tool in dev_env.tools:
            all_required_tool_images.add(tool["image_name"] + ":" + tool["image_version"])

    deleted_dev_env_tool_images = set()
    for tool in deleted_dev_env.tools:
        deleted_dev_env_tool_images.add(tool["image_name"] + ":" + tool["image_version"])

    for tool_image in deleted_dev_env_tool_images:
        if tool_image not in all_required_tool_images:
            try_to_delete_tool_image(tool_image, dev_env_local_setup)

def execute(dev_env_name: str) -> None:
    platform = DevEnvLocalSetup()
    dev_env_to_delete = platform.get_dev_env_by_name(dev_env_name)

    if dev_env_to_delete is None:
        stderr.print("[red]Error: The [bold]" + dev_env_name + "[/bold] Development Environment doesn't exist.")
    else:
        stdout.print("Deleting the Development Environment...")
        platform.local_dev_envs.remove(dev_env_to_delete)
        platform.flush_to_file()

        remove_unused_tool_images(dev_env_to_delete, platform)
        stdout.print("[green]Successfully deleted the " + dev_env_name + "![/]")