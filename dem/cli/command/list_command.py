"""list CLI command implementation."""
# dem/cli/list_command.py

from dem.core import container_engine, data_management, dev_env_setup, registry
from dem.cli.console import stdout, stderr
from rich.table import Table

(
    DEV_ENV_ORG_NOT_IN_REGISTRY,
    DEV_ENV_ORG_INSTALLED_LOCALLY,
    DEV_ENV_ORG_REAINSTALL,
    DEV_ENV_ORG_READY,
) = range(4)

(
    DEV_ENV_LOCAL_NOT_AVAILABLE,
    DEV_ENV_LOCAL_REINSTALL,
    DEV_ENV_LOCAL_INSTALLED,
) = range(3)

dev_env_org_status_messages = {
    DEV_ENV_ORG_NOT_IN_REGISTRY: "[red]Error: Required image is not available in the registry![/]",
    DEV_ENV_ORG_INSTALLED_LOCALLY: "Installed locally.",
    DEV_ENV_ORG_REAINSTALL: "Incopmlete local install. Reinstall needed.",
    DEV_ENV_ORG_READY: "Ready to install.",
}

dev_env_local_status_messages = {
    DEV_ENV_LOCAL_NOT_AVAILABLE: "[red]Error: Required image is not available![/]",
    DEV_ENV_LOCAL_REINSTALL: "Incopmlete local install. Reinstall needed.",
    DEV_ENV_LOCAL_INSTALLED: "Installed.",
}

def is_dev_env_org_installed_locally(dev_env_org: dev_env_setup.DevEnvOrg) -> bool:
    dev_env_json_deserialized = data_management.get_deserialized_dev_env_json()
    dev_env_local_setup_obj = dev_env_setup.DevEnvLocalSetup(dev_env_json_deserialized)
    return dev_env_org.is_installed_locally(dev_env_local_setup_obj)

def get_dev_env_status(dev_env: [dev_env_setup.DevEnvLocal, dev_env_setup.DevEnvOrg],
                       local_images: list, registry_images: list) -> str:
    image_statuses = dev_env.check_image_availability(local_images, registry_images)
    dev_env_status = ""
    if isinstance(dev_env, dev_env_setup.DevEnvOrg):
        if (dev_env_setup.IMAGE_NOT_AVAILABLE in image_statuses) or (dev_env_setup.IMAGE_LOCAL_ONLY in image_statuses):
            dev_env_status = dev_env_org_status_messages[DEV_ENV_ORG_NOT_IN_REGISTRY]
        elif (image_statuses.count(dev_env_setup.IMAGE_LOCAL_AND_REGISTRY) == len(image_statuses)) and \
                (is_dev_env_org_installed_locally(dev_env) == True):
            dev_env_status = dev_env_org_status_messages[DEV_ENV_ORG_INSTALLED_LOCALLY]
        else:
            if (is_dev_env_org_installed_locally(dev_env) == True):
                dev_env_status = dev_env_org_status_messages[DEV_ENV_ORG_REAINSTALL]
            else:
                dev_env_status = dev_env_org_status_messages[DEV_ENV_ORG_READY]
    else:
        if (dev_env_setup.IMAGE_NOT_AVAILABLE in image_statuses):
            dev_env_status = dev_env_local_status_messages[DEV_ENV_LOCAL_NOT_AVAILABLE]
        elif (dev_env_setup.IMAGE_REGISTRY_ONLY in image_statuses):
            dev_env_status = dev_env_local_status_messages[DEV_ENV_LOCAL_REINSTALL]
        else:
            dev_env_status = dev_env_local_status_messages[DEV_ENV_LOCAL_INSTALLED]
    return dev_env_status

def execute(local: bool, all: bool, env: bool) -> None:
    if ((local == True) or (all == True)) and (env == True):
        dev_env_setup_obj = None
        if ((local == True) and (all == False)):
            dev_env_json_deserialized = data_management.get_deserialized_dev_env_json()
            dev_env_setup_obj = dev_env_setup.DevEnvLocalSetup(dev_env_json_deserialized)
            if not dev_env_setup_obj.dev_envs:
                stdout.print("[yellow]No installed Development Environments.[/]")
                return
        elif((local == False) and (all==True)):
            dev_env_org_json_deserialized = data_management.get_deserialized_dev_env_org_json()
            dev_env_setup_obj = dev_env_setup.DevEnvOrgSetup(dev_env_org_json_deserialized)
        else:
            stderr.print("Error: This command is not yet supported.")
            return
        
        container_engine_obj = container_engine.ContainerEngine()
        local_images = container_engine_obj.get_local_image_tags()
        registry_images = registry.list_repos()

        table = Table()
        table.add_column("Development Environment")
        table.add_column("Status")
        for dev_env_org in dev_env_setup_obj.dev_envs:
            table.add_row(dev_env_org.name, get_dev_env_status(dev_env_org, 
                                                               local_images,
                                                               registry_images))
        stdout.print(table)
    else:
        stderr.print(\
"""Usage: dem list [OPTIONS]
Try 'dem list --help' for help.

Error: You need to set the scope and what to list!""")