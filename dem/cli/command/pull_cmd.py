"""The pull command"""
# dem/cli/command/pull_cmd.py

from dem.core import dev_env_setup as dev_env_setup, \
                     data_management as data_management, \
                     container_engine as container_engine, \
                     registry as registry
from dem.cli.console import stdout, stderr

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

    #Check that the Dev Env is already installed in the dev_env.json file.
    if isinstance(dev_env_local, dev_env_setup.DevEnvLocal):
        # Look for any difference between the local and the org Dev Env.
        if dev_env_local.tools != dev_env_org.tools:
            dev_env_local_setup.dev_envs.remove(dev_env_local)
            dev_env_local.tools = dev_env_org.tools
            dev_env_local_setup.dev_envs.append(dev_env_local)
            deserialized_local_dev_env = dev_env_local_setup.get_deserialized()
            data_management.write_deserialized_dev_env_json(deserialized_local_dev_env)
        else:
            # The local and in org instance are the same.
            pass
    else:
        # If not available, install it.
        dev_env_local = dev_env_setup.DevEnvLocal(dev_env_org=dev_env_org)
        dev_env_local_setup.dev_envs.append(dev_env_local)
        deserialized_local_dev_env = dev_env_local_setup.get_deserialized()
        data_management.write_deserialized_dev_env_json(deserialized_local_dev_env)

    #The local DevEnvSetup contains the DevEnvOrg to install. Check the images' status
    container_engine_obj = container_engine.ContainerEngine()
    local_images = container_engine_obj.get_local_image_tags()
    registry_images = registry.list_repos()
    dev_env_local.check_image_availability(local_images, registry_images)

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
        stdout.print("The [yellow]" + dev_env_local.name + "[/] Development Environment is ready!")
    else:
        stderr.print("The istallation failed.")