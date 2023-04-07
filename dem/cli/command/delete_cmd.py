"""delete CLI command implementation."""
# dem/cli/command/delete_cmd.py

from dem.core.data_management import read_deserialized_dev_env_json, write_deserialized_dev_env_json
from dem.core.dev_env_setup import DevEnvLocalSetup, DevEnvLocal
from dem.core.container_engine import ContainerEngine
import typer

def remove_unused_tool_images(deleted_dev_env: DevEnvLocal, dev_env_local_setup: DevEnvLocalSetup) -> None:
    required_tool_images = set()
    for dev_env in dev_env_local_setup.dev_envs:
        for tool in dev_env.tools:
            required_tool_images.add(tool["image_name"] + ":" + tool["image_version"])

    container_engine = ContainerEngine()
    for tool in deleted_dev_env.tools:
        tool_image = tool["image_name"] + ":" + tool["image_version"]
        if tool_image not in required_tool_images:
            if typer.confirm(tool_image + " is not required by any Development Environment. \
                             Would you like to remove it?"):
                container_engine.remove(tool_image)

def execute(dev_env_name: str) -> None:
    deserialized_dev_env_json = read_deserialized_dev_env_json()
    dev_env_local_setup = DevEnvLocalSetup(deserialized_dev_env_json)
    dev_env_to_delete = dev_env_local_setup.get_dev_env_by_name(dev_env_name)
    dev_env_local_setup.dev_envs.remove(dev_env_to_delete)
    deserialized_dev_env_json = dev_env_local_setup.get_deserialized()
    write_deserialized_dev_env_json(deserialized_dev_env_json)

    remove_unused_tool_images(dev_env_to_delete, dev_env_local_setup)