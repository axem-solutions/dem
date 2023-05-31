"""delete CLI command implementation."""
# dem/cli/command/delete_cmd.py

from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal
from dem.cli.console import stderr, stdout
import typer
import docker.errors

def try_to_delete_tool_image(tool_image: str, dev_env_local_setup: DevEnvLocalSetup):
    stdout.print("\nThe tool image [bold]" + tool_image + "[/bold] is not required by any Development Environment anymore.")
    if typer.confirm("Would you like to remove it?"):
        pass
        # try:
        #     dev_env_local_setup.container_engine.remove(tool_image)
        # except docker.errors.ImageNotFound:
        #     stdout.print("[yellow]Couldn't delete " + tool_image + ", because doesn't exist.")
        # except docker.errors.APIError:
        #     stderr.print("[red]Error: " + tool_image + " is used by a container. Unable to remove it.")

def remove_unused_tool_images(deleted_dev_env: DevEnvLocal, dev_env_local_setup: DevEnvLocalSetup) -> None:
    all_required_tool_images = set()
    for dev_env in dev_env_local_setup.dev_envs:
        for tool in dev_env.tools:
            all_required_tool_images.add(tool["image_name"] + ":" + tool["image_version"])

    deleted_dev_env_tool_images = set()
    for tool in deleted_dev_env.tools:
        deleted_dev_env_tool_images.add(tool["image_name"] + ":" + tool["image_version"])

    for tool_image in deleted_dev_env_tool_images:
        if tool_image not in all_required_tool_images:
            try_to_delete_tool_image(tool_image, dev_env_local_setup)

def execute(dev_env_name: str) -> None:
    dev_env_local_setup = DevEnvLocalSetup()
    dev_env_to_delete = dev_env_local_setup.get_dev_env_by_name(dev_env_name)

    if dev_env_to_delete is None:
        stderr.print("[red]The Development Environment doesn't exist.")
    else:
        dev_env_local_setup.dev_envs.remove(dev_env_to_delete)
        dev_env_local_setup.update_json()

        remove_unused_tool_images(dev_env_to_delete, dev_env_local_setup)