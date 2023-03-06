"""list CLI command implementation."""
# dem/cli/list_command.py

from dem.core import container_engine, data_management, dev_env_setup, registry
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

(
    LOCAL_ONLY,
    REGISTRY_ONLY,
    LOCAL_AND_REGISTRY,
    NOT_AVAILABLE,
) = range(4)

def check_image_availability(tool: dict, local_images: list = [], registry_images: list = []):
    image_status = NOT_AVAILABLE
    tool_image = tool["image_name"] + ':' + tool["image_version"]
    if tool_image in local_images:
        image_status = LOCAL_ONLY
    if tool_image in registry_images:
        if image_status == LOCAL_ONLY:
            image_status = LOCAL_AND_REGISTRY
        else:
            image_status = REGISTRY_ONLY
    return image_status


def execute(local: bool, all: bool, env: bool) -> None:
    if (local == True) and (env == True):
        dev_env_json_deserialized = data_management.get_deserialized_dev_env_json()
        dev_env_setup_instance = dev_env_setup.DevEnvSetup(dev_env_json_deserialized)
        container_engine_obj = container_engine.ContainerEngine()
        local_images = container_engine_obj.get_local_image_tags()

        if dev_env_setup_instance.dev_envs:
            print_list_table(dev_env_setup_instance.dev_envs, local_images)
        else:
            stdout.print("[yellow]No installed Development Environments.[/]")
    elif (all == True) and (env == True):
        dev_env_org_json_deserialized = data_management.get_deserialized_dev_env_org_json()
        dev_env_org_setup_obj = dev_env_setup.DevEnvOrgSetup(dev_env_org_json_deserialized)
        dev_env_json_deserialized = data_management.get_deserialized_dev_env_json()
        dev_env_setup_instance = dev_env_setup.DevEnvSetup(dev_env_json_deserialized)
        container_engine_obj = container_engine.ContainerEngine()
        local_images = container_engine_obj.get_local_image_tags()
        registry_images = registry.list_repos()
        table = Table()
        table.add_column("Development Environment")
        table.add_column("Status")

        for dev_env_org in dev_env_org_setup_obj.dev_envs_in_org:
            image_statuses = []
            for tool in dev_env_org.tools:
                image_statuses.append(check_image_availability(tool, local_images, registry_images))

            dev_env_status = ""
            if (NOT_AVAILABLE in image_statuses) or (LOCAL_ONLY in image_statuses):
                dev_env_status = "[red]Error: Required image is not available in the registry![/]"
            elif (image_statuses.count(LOCAL_AND_REGISTRY) == len(image_statuses)) and \
                 (dev_env_org.is_installed_locally(dev_env_setup_instance) == True):
                dev_env_status = "Installed locally."
            else:
                if (dev_env_org.is_installed_locally(dev_env_setup_instance) == True):
                    dev_env_status = "Incopmlete local install. Reinstall needed."
                else:
                    dev_env_status = "Ready to install."

            table.add_row(dev_env_org.name, dev_env_status)
            
        stdout.print(table)

    else:
        stderr.print(\
"""Usage: dem list [OPTIONS]
Try 'dem list --help' for help.

Error: You need to set the scope and what to list!""")