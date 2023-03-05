"""list CLI command implementation."""
# dem/cli/list_command.py

from dem.core import container_engine, data_management, dev_env_setup
from dem.cli.console import stdout, stderr
from rich.table import Table

def print_list_table(dev_envs: list, local_image_tags: list) -> None:
    table = Table()
    table.add_column("Development Environment")
    table.add_column("Status")

    for dev_env in dev_envs:
        dev_env.validate(local_image_tags)
        for tool in dev_env.tools:
            if tool["is_image_available"] == False:
                print_validation_result = "[red]✗ Missing images[/]"
                break
        else:
            print_validation_result = "[green]✓[/]"
        table.add_row(dev_env.name, print_validation_result)

    stdout.print(table)

def execute(local: bool, env: bool) -> None:
    if (local == True) and (env == True):
        dev_env_json_deserialized = data_management.get_deserialized_dev_env_json()
        dev_env_setup_instance = dev_env_setup.DevEnvSetup(dev_env_json_deserialized)
        local_image_tags = container_engine.get_local_image_tags()

        if dev_env_setup_instance.dev_envs:
            print_list_table(dev_env_setup_instance.dev_envs, local_image_tags)
        else:
            stdout.print("[yellow]No installed Development Environments.[/]")
    else:
        stderr.print(\
"""Usage: dem list [OPTIONS]
Try 'dem list --help' for help.

Error: You need to set the scope and what to list!""")