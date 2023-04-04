"""info CLI command implementation."""
# dem/cli/command/info_cmd.py

from dem.core import container_engine, data_management, dev_env_setup, registry
from dem.cli.console import stdout, stderr
from rich.table import Table

image_status_messages = {
    dev_env_setup.IMAGE_NOT_AVAILABLE: "[red]Error: Image is not available.[/]",
    dev_env_setup.IMAGE_LOCAL_ONLY: "Image is available locally.",
    dev_env_setup.IMAGE_REGISTRY_ONLY: "Image is available in the registry.",
    dev_env_setup.IMAGE_LOCAL_AND_REGISTRY: "Image is available locally and in the registry.",
}

def print_info(dev_env: (dev_env_setup.DevEnvLocal | dev_env_setup.DevEnvOrg)) -> None:
    tool_info_table = Table()
    tool_info_table.add_column("Type")
    tool_info_table.add_column("Image")
    tool_info_table.add_column("Status")
    for tool in dev_env.tools:
        tool_info_table.add_row(tool["type"], tool["image_name"] + ':' + tool["image_version"],
                                image_status_messages[tool["image_status"]])
    stdout.print(tool_info_table)

def find_dev_env(dev_envs: list, dev_env_name_to_find: str) -> (dev_env_setup.DevEnvLocal | dev_env_setup.DevEnvOrg | None):
    for dev_env in dev_envs:
        if dev_env.name == dev_env_name_to_find:
            return dev_env

def update_image_status(dev_env: (dev_env_setup.DevEnvLocal | dev_env_setup.DevEnvOrg)) -> None:
    # This functions must be called, so the tools in the dev env get updated.
    dev_env.check_image_availability()

def execute(arg_dev_env_name: str) -> None:
    dev_env_json_deserialized = data_management.read_deserialized_dev_env_json()
    dev_env_setup_local_obj = dev_env_setup.DevEnvLocalSetup(dev_env_json_deserialized)

    dev_env_json_deserialized = data_management.read_deserialized_dev_env_org_json()
    dev_env_setup_org_obj = dev_env_setup.DevEnvOrgSetup(dev_env_json_deserialized)

    dev_env = find_dev_env(dev_env_setup_local_obj.dev_envs, arg_dev_env_name)
    if dev_env == None:
        dev_env = find_dev_env(dev_env_setup_org_obj.dev_envs, arg_dev_env_name)
    if dev_env == None:
        stderr.print("[red]Error: Unknown Development Environment: " + arg_dev_env_name + "[/]")
        return
    else:
        update_image_status(dev_env)
        print_info(dev_env)