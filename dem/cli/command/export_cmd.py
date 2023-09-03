"""export CLI command implementation."""
# dem/cli/command/export_cmd.py


import re
from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stderr
import json, os

def check_is_directory(param: str):
     if None != param:
        return(os.path.isdir(param))     
     else:
        return False
     
def check_is_path_contains_spec_char(param: str):
    special_chars=re.compile('[~/\^]')
    if None != param:
        if None != special_chars.search(param):
            return True
        else:
            return False
    else:
        return False
    
def create_exported_dev_env_json(dev_env_name: str,dev_env_json: str,given_path: str):
    
    file_name=None
    file_path=None

    if True == check_is_directory(given_path):
        file_name=dev_env_name
        file_path=given_path+"/"
    elif True == check_is_path_contains_spec_char(given_path):        
        file_name=""
        file_path=given_path         
    elif None != given_path:
        file_name=given_path        
        file_path=""    
    else:
        file_name=dev_env_name        
        file_path=""
    
    exported_file = open(file_path+file_name, "w")        
    json.dump(dev_env_json, exported_file, indent=4)
    exported_file.close()        

def execute(dev_env_name: str, path_to_export: str) -> None:
    platform = DevEnvLocalSetup()
    dev_env_to_export = platform.get_dev_env_by_name(dev_env_name)

    if dev_env_to_export is not None:                
        create_exported_dev_env_json(dev_env_name,dev_env_to_export.__dict__,path_to_export)                
    else:
        stderr.print("[red]Error: The input Development Environment does not exist.[/]")