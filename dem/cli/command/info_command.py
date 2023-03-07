"""info CLI command implementation."""
# dem/cli/command/info_command.py

from dem.core import container_engine, data_management, dev_env_setup
from dem.cli.console import stdout, stderr
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

    stdout.print(tool_info_table)

def execute(arg_dev_env_name: str) -> None:
    dev_env_json_deserialized = data_management.get_deserialized_dev_env_json()
    dev_env_setup_instance = dev_env_setup.DevEnvLocalSetup(dev_env_json_deserialized)
    container_engine_obj = container_engine.ContainerEngine()
    local_image_tags = container_engine_obj.get_local_image_tags()

    for dev_env in dev_env_setup_instance.dev_envs:
        if dev_env.name == arg_dev_env_name:
            print_info(dev_env, local_image_tags)
            break
    else:
        stderr.print("[red]Error: Unknown Development Environment: " + arg_dev_env_name + "[/]")