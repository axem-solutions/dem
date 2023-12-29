"""load CLI command implementation."""
# dem/cli/command/load_cmd.py

from dem.core.dev_env import DevEnv
from dem.core.platform import Platform
from dem.cli.console import stderr
import json, os

def check_is_file_exist(param: str | None) -> bool:
    if param is not None:
        return(os.path.isfile(param))     
    else:
        return False

def load_dev_env_to_dev_env_json(dev_env_local_setup: Platform,path_to_dev_env: str) -> bool:
    raw_file = open(path_to_dev_env, "r")   
            
    try:
        dev_env = json.load(raw_file)
        
        if dev_env_local_setup.get_dev_env_by_name(dev_env["name"]) is not None:
            stderr.print("[red]Error: The Development Environment exist.[/]")
            return False                       
        else:        
            new_dev_env = DevEnv(dev_env)
            dev_env_local_setup.local_dev_envs.append(new_dev_env)
    except json.decoder.JSONDecodeError:
       stderr.print("[red]Error: invalid json format.[/]")
       return False                       
    else:
        raw_file.close()
        return True

def execute(platform: Platform, path_to_dev_env: str) -> None:
    if check_is_file_exist(path_to_dev_env) is True:                
        retval = load_dev_env_to_dev_env_json(platform,path_to_dev_env)        
        if retval == True:
            platform.flush_descriptors()
    else:
        stderr.print("[red]Error: The input file does not exist.[/]")