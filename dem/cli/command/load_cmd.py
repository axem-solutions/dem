"""load CLI command implementation."""
# dem/cli/command/load_cmd.py

from dem.core.dev_env_setup import DevEnvLocal, DevEnvLocalSetup
from dem.cli.console import stderr
import json, os

def check_is_file_exist(param: str) -> bool:
    if None != param:
        return(os.path.isfile(param))     
    else:
        return False

def load_dev_env_to_dev_env_json(dev_env_local_setup: DevEnvLocalSetup,path_to_dev_env: str) -> bool:
    raw_file = open(path_to_dev_env, "r")   
            
    try:
        dev_env = json.load(raw_file)
        
        if dev_env_local_setup.get_dev_env_by_name(dev_env["name"]) is not None:
            stderr.print("[red]Error: The Development Environment exist.[/]")
            return False                       
        else:        
            new_dev_env = DevEnvLocal(dev_env)
            dev_env_local_setup.dev_envs.append(new_dev_env)
            new_dev_env.check_image_availability(dev_env_local_setup.tool_images)
            dev_env_local_setup.pull_images(new_dev_env.tools)
    except json.decoder.JSONDecodeError:
       stderr.print("[red]Error: invalid json format.[/]")
       return False                       
    else:
        raw_file.close()
        return True

def execute(path_to_dev_env: str) -> None:
    dev_env_local_setup = DevEnvLocalSetup()    

    if check_is_file_exist(path_to_dev_env) is True:                
        retval = load_dev_env_to_dev_env_json(dev_env_local_setup,path_to_dev_env)        
        if retval == True:
            dev_env_local_setup.update_json()                
        else:
            stderr.print("[red]Error: Something went wrong.[/]")    
    else:
        stderr.print("[red]Error: The input file does not exist.[/]")