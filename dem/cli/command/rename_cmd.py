"""rename CLI command implementation."""
# dem/cli/command/rename_cmd.py

from dem.core.dev_env_setup import DevEnvLocal, DevEnvLocalSetup
import dem.core.data_management as data_management


def dev_env_name_check(dev_env_local_setup: DevEnvLocalSetup, dev_env_name: str) -> (DevEnvLocal | None):
    for dev_env in dev_env_local_setup.dev_envs:
        if dev_env.name == dev_env_name:
            return dev_env


def execute(dev_env_name: str, new_dev_end_name: str) -> None:
    derserialized_local_dev_nev = data_management.read_deserialized_dev_env_json()
    dev_env_local_setup = DevEnvLocalSetup(derserialized_local_dev_nev)
    dev_env_original = dev_env_name_check(dev_env_local_setup, dev_env_name)
    if dev_env_original is None:
        print("The " + dev_env_name + " not found")

    derserialized_local_dev_nev = dev_env_local_setup.get_deserialized()
    #print(derserialized_local_dev_nev["development_environments"][2]["name"])
    for devenv in derserialized_local_dev_nev["development_environments"]:
        print (devenv["name"])
        if devenv["name"] == dev_env_name:
            devenv["name"] = new_dev_end_name
    
    for devenv in derserialized_local_dev_nev["development_environments"]:
        print (devenv["name"])
    
    data_management.write_deserialized_dev_env_json(derserialized_local_dev_nev)

        