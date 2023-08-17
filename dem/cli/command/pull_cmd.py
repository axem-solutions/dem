"""The pull command"""
# dem/cli/command/pull_cmd.py

from dem.core import dev_env_setup as dev_env_setup, \
                     registry as registry
from dem.core.tool_images import ToolImages
from dem.cli.console import stdout, stderr

def install_to_dev_env_json(dev_env_local: dev_env_setup.DevEnvLocal, 
                            dev_env_org: dev_env_setup.DevEnvOrg,
                            dev_env_local_setup: dev_env_setup.DevEnvLocalSetup) -> dev_env_setup.DevEnvLocal:
    """Install the Dev Env descriptor to the dev_env.json.
    
    If the dev_env_local is None, the Dev Env is not yet installed locally. Install it by appending 
    the Dev Env descriptor to the dev_env.json file.
    If the Dev Env is already installed, but the descriptor is different, then overwrite the 
    dev_env.json element with the new one.
    If the Dev Env is already installed and both the descriptors are the same, then there is nothing
    to do. 
    Args:
        dev_env_local -- local Dev Env instance (none if not yet installed)
        dev_env_org -- organization's Dev Env instance
        dev_env_local_setup -- the local Dev Env setup
    Return with the dev_env_local instance.
    """
    if dev_env_local is None:
        # If not available, install it.
        dev_env_local = dev_env_setup.DevEnvLocal(dev_env_org=dev_env_org)
        dev_env_local_setup.dev_envs.append(dev_env_local)
        dev_env_local_setup.flush_to_file()
    elif dev_env_local.tools != dev_env_org.tools:
        # If already installed, but different, then overwrite it.
        dev_env_local.tools = dev_env_org.tools
        dev_env_local_setup.flush_to_file()

    return dev_env_local

def execute(dev_env_name: str) -> None:
    # Get the organization's Dev Env if available.
    dev_env_org_setup = dev_env_setup.DevEnvOrgSetup()
    dev_env_org = dev_env_org_setup.get_dev_env_by_name(dev_env_name)
    if dev_env_org is None:
        stderr.print("[red]Error: The input Development Environment is not available for the organization.[/]")
        return

    dev_env_local_setup = dev_env_setup.DevEnvLocalSetup()
    dev_env_local = dev_env_org.get_local_instance(dev_env_local_setup)
    dev_env_local = install_to_dev_env_json(dev_env_local, dev_env_org, dev_env_local_setup)

    # The local Dev Env setup contains the DevEnvOrg to install. Check the images' statuses
    dev_env_local.check_image_availability(dev_env_local_setup.tool_images)
    dev_env_local_setup.pull_images(dev_env_local.tools)
    # Check image availability again.
    image_statuses = dev_env_local.check_image_availability(dev_env_local_setup.tool_images, 
                                                            update_tool_images=True)

    if image_statuses.count(ToolImages.LOCAL_AND_REGISTRY) == len(image_statuses):
        stdout.print("The [yellow]" + dev_env_local.name + "[/] Development Environment is ready!")
    else:
        stderr.print("The installation failed.")