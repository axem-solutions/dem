"""clone CLI command implementation."""
# dem/cli/command/rename_cmd.py

import copy
from dem.core.dev_env import DevEnv
from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stderr

def get_dev_env_to_clone(platform: DevEnvLocalSetup, dev_env_name: str) -> (DevEnv | None):
    dev_env_to_clone = platform.get_dev_env_by_name(dev_env_name) 

    if dev_env_to_clone is None:
        stderr.print("[red]Error: The input Development Environment does not exist.[/]")
        return None
    else:
        return dev_env_to_clone

def check_new_dev_env_name_taken(dev_env_local_setup: DevEnvLocalSetup, new_dev_env_name: str) -> bool:
    if dev_env_local_setup.get_dev_env_by_name(new_dev_env_name):
        stderr.print("[red]Error: Development environment already exists with the " + new_dev_env_name + " name.[/]")
        return True
    else:
        return False

def clone_given_dev_env(platform: DevEnvLocalSetup, dev_env_to_clone: DevEnv,
                        new_dev_env_name: str):
    new_dev_env = copy.deepcopy(dev_env_to_clone)
    new_dev_env.name = new_dev_env_name
    platform.local_dev_envs.append(new_dev_env)
    platform.flush_to_file()

def execute(dev_env_to_clone_name: str, new_dev_env_name: str) -> None:
    platform = DevEnvLocalSetup()
    dev_env_to_clone = get_dev_env_to_clone(platform, dev_env_to_clone_name)

    if (dev_env_to_clone is not None and
        check_new_dev_env_name_taken(platform,new_dev_env_name) is False):
        clone_given_dev_env(platform, dev_env_to_clone, new_dev_env_name)