import dem.core.data_management as data_management
import dem.core.dev_env_setup as dev_env_setup
import docker 
from rich.console import Console
from rich.table import Table

def print_info(dev_env: dev_env_setup.DevEnv, local_image_tags: list):
    tool_info_table = Table()
    tool_info_table.add_column("Type")
    tool_info_table.add_column("Image")

    dev_env.validate(local_image_tags)

    for tool in dev_env.tools:
        if tool["is_image_available"] == True:
            tool_info_table.add_row(tool["type"], tool["image_name"] + ':' + tool["image_version"])
        else:
            tool_info_table.add_row(tool["type"], "[red]Error: missing image![/]")

    console = Console()
    console.print(tool_info_table)

def execute(dev_env_name: str) -> None:
    dev_env_json_deserialized = data_management.get_deserialized_dev_env_json()
    dev_env_setup_instance = dev_env_setup.DevEnvSetup(dev_env_json_deserialized)

    docker_client = docker.from_env()

    local_image_tags = []

    for image in docker_client.images.list():
        for tag in image.tags:
            local_image_tags.append(tag)

    for dev_env in dev_env_setup_instance.dev_envs:
        if dev_env.name == dev_env_name:
            print_info(dev_env, local_image_tags)