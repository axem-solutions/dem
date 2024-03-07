"""cp CLI command implementation."""
# dem/cli/command/rename_cmd.py

import copy
from dem.core.dev_env import DevEnv
from dem.core.platform import Platform
from dem.cli.console import stderr

def get_dev_env_to_cp(platform: Platform, dev_env_name: str) -> (DevEnv | None):
    dev_env_to_cp = platform.get_dev_env_by_name(dev_env_name) 

    if dev_env_to_cp is None:
        stderr.print("[red]Error: The input Development Environment does not exist.[/]")
        return None
    else:
        return dev_env_to_cp

def check_new_dev_env_name_taken(dev_env_local_setup: Platform, new_dev_env_name: str) -> bool:
    if dev_env_local_setup.get_dev_env_by_name(new_dev_env_name):
        stderr.print("[red]Error: Development environment already exists with the " + new_dev_env_name + " name.[/]")
        return True
    else:
        return False

def cp_given_dev_env(platform: Platform, dev_env_to_cp: DevEnv,
                        new_dev_env_name: str):
    new_dev_env = copy.deepcopy(dev_env_to_cp)
    new_dev_env.name = new_dev_env_name
    new_dev_env.is_installed = False
    platform.local_dev_envs.append(new_dev_env)
    platform.flush_descriptors()

def execute(platform: Platform, dev_env_to_cp_name: str, new_dev_env_name: str) -> None:
    dev_env_to_cp = get_dev_env_to_cp(platform, dev_env_to_cp_name)

    if (dev_env_to_cp is not None and
        check_new_dev_env_name_taken(platform,new_dev_env_name) is False):
        cp_given_dev_env(platform, dev_env_to_cp, new_dev_env_name)