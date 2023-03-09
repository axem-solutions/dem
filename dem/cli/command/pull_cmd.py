"""The pull command"""
# dem/cli/command/pull_cmd.py

from dem.core import dev_env_setup as dev_env_setup, \
                     data_management as data_management, \
                     container_engine as container_engine, \
                     registry as registry
from dem.cli.console import stdout, stderr

<<<<<<< HEAD
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
=======
def execute(dev_env_name: str) -> None:
    #Get the organization's Dev Env if available.
    dev_env_org_json_deserialized = data_management.get_deserialized_dev_env_org_json()
    dev_env_org_setup = dev_env_setup.DevEnvOrgSetup(dev_env_org_json_deserialized)
    for dev_env_org in dev_env_org_setup.dev_envs:
        if dev_env_org.name == dev_env_name:
            break
    else:
        stderr.print("[red]Error: The input Development Environment is not available for the organization.[/]")
        return
    

    dev_env_local_json_deserialized = data_management.get_deserialized_dev_env_json()
    dev_env_local_setup = dev_env_setup.DevEnvLocalSetup(dev_env_local_json_deserialized)
    dev_env_local = dev_env_org.get_local_instance(dev_env_local_setup)

    #Check that the Dev Env is already installed in the dev_env.json file.
    if isinstance(dev_env_local, dev_env_setup.DevEnvLocal):
        # Look for any difference between the local and the org Dev Env.
        if dev_env_local.tools != dev_env_org.tools:
            dev_env_local_setup.dev_envs.remove(dev_env_local)
            dev_env_local.tools = dev_env_org.tools
            dev_env_local_setup.dev_envs.append(dev_env_local)
            deserialized_local_dev_env = dev_env_local_setup.get_deserialized()
            data_management.write_dev_env_json(deserialized_local_dev_env)
        else:
            # The local and in org instance are the same.
            pass
    else:
>>>>>>> 9ea2523 ('dem pull DEV_ENV_NAME' implemented. Only tested with already installed Dev Env.)
        # If not available, install it.
        dev_env_local = dev_env_setup.DevEnvLocal(dev_env_org=dev_env_org)
        dev_env_local_setup.dev_envs.append(dev_env_local)
        deserialized_local_dev_env = dev_env_local_setup.get_deserialized()
<<<<<<< HEAD
        data_management.write_deserialized_dev_env_json(deserialized_local_dev_env)
    elif dev_env_local.tools != dev_env_org.tools:
        # If already installed, but different, then overwrite it.
        dev_env_local_setup.dev_envs.remove(dev_env_local)
        dev_env_local.tools = dev_env_org.tools
        dev_env_local_setup.dev_envs.append(dev_env_local)
        deserialized_local_dev_env = dev_env_local_setup.get_deserialized()
        data_management.write_deserialized_dev_env_json(deserialized_local_dev_env)

    return dev_env_local

def pull_registry_only_images(dev_env_local: dev_env_setup.DevEnvLocal,
                              container_engine_obj: container_engine.ContainerEngine) -> None:
    """Pull images that are only present in the registry.
    
    Args:
        dev_env_local -- local Dev Env instance
        container_engine_obj -- interface to communicate with the container engine
    """
    for tool in dev_env_local.tools:
        if tool["image_status"] == dev_env_setup.IMAGE_REGISTRY_ONLY:
            image_to_pull = tool["image_name" ] + ':' + tool["image_version"]
            stdout.print("Pulling image: " + image_to_pull)
            container_engine_obj.pull(image_to_pull)

def execute(dev_env_name: str) -> None:
    #Get the organization's Dev Env if available.
    dev_env_org_json_deserialized = data_management.read_deserialized_dev_env_org_json()
    dev_env_org_setup = dev_env_setup.DevEnvOrgSetup(dev_env_org_json_deserialized)
    dev_env_org = dev_env_org_setup.get_dev_env(dev_env_name)
    if dev_env_org is None:
        stderr.print("[red]Error: The input Development Environment is not available for the organization.[/]")
        return

    dev_env_local_json_deserialized = data_management.read_deserialized_dev_env_json()
    dev_env_local_setup = dev_env_setup.DevEnvLocalSetup(dev_env_local_json_deserialized)
    dev_env_local = dev_env_org.get_local_instance(dev_env_local_setup)

    dev_env_local = install_to_dev_env_json(dev_env_local, dev_env_org, dev_env_local_setup)

    #The local DevEnvSetup contains the DevEnvOrg to install. Check the images' status
    container_engine_obj = container_engine.ContainerEngine()
    local_images = container_engine_obj.get_local_tool_images()
    registry_images = registry.list_repos()
    dev_env_local.check_image_availability(local_images, registry_images)

    pull_registry_only_images(dev_env_local, container_engine_obj)

    local_images = container_engine_obj.get_local_tool_images()
    image_statuses = dev_env_local.check_image_availability(local_images, registry_images)

    if image_statuses.count(dev_env_setup.IMAGE_LOCAL_AND_REGISTRY) == len(image_statuses):
        stdout.print("The [yellow]" + dev_env_local.name + "[/] Development Environment is ready!")
=======
        data_management.write_dev_env_json(deserialized_local_dev_env)

    #The local DevEnvSetup contains the DevEnvOrg to install. Check the images' status
    container_engine_obj = container_engine.ContainerEngine()
    local_images = container_engine_obj.get_local_image_tags()
    registry_images = registry.list_repos()
    image_statuses = dev_env_local.check_image_availability(local_images, registry_images)

    # Pull the registry only images.
    for tool in dev_env_local.tools:
        if tool["image_status"] == dev_env_setup.IMAGE_REGISTRY_ONLY:
            image_to_pull = tool["image_name" ] + ':' + tool["image_version"]
            stdout.print("Pulling image: " + image_to_pull)
            container_engine_obj.pull(image_to_pull)


    #Tmp validation:
    local_images = container_engine_obj.get_local_image_tags()
    image_statuses = dev_env_local.check_image_availability(local_images, registry_images)

    if image_statuses.count(dev_env_setup.IMAGE_LOCAL_AND_REGISTRY) == len(image_statuses):
<<<<<<< HEAD
        stdout.print("Succesfull install!")
>>>>>>> 9ea2523 ('dem pull DEV_ENV_NAME' implemented. Only tested with already installed Dev Env.)
=======
        stdout.print("The [yellow]" + dev_env_local.name + "[/] Development Environment is ready!")
>>>>>>> c36cb35 (Writing the updated local Dev Env into the dev_env.json file. Minor fix in the deserialization member function. The images are now used with the axemsolution Docker Hub registry in their name.)
    else:
        stderr.print("The istallation failed.")