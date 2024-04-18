"""import CLI command implementation."""
# dem/cli/command/import_cmd.py

from dem.core.dev_env import DevEnv
from dem.core.platform import Platform
from dem.cli.console import stderr
import json, os
import typer

def import_dev_env_from_json(platform: Platform,path_to_dev_env: str) -> None:
    """ Import a Development Environment from a JSON file.
    
        Args:
            platform (Platform): The platform instance.
            path_to_dev_env (str): The path to the JSON file.
            
        Raises:
            typer.Abort: If the Development Environment already exists, or the JSON format is 
            invalid.
    """
    raw_file = open(path_to_dev_env, "r")   
            
    try:
        dev_env_descriptor_to_import = json.load(raw_file)
        
        if platform.get_dev_env_by_name(dev_env_descriptor_to_import["name"]) is not None:
            stderr.print("[red]Error: The Development Environment already exists.[/]")
            raise typer.Abort()
        else:        
            new_dev_env: DevEnv = DevEnv(dev_env_descriptor_to_import)
            platform.local_dev_envs.append(new_dev_env)
    except json.decoder.JSONDecodeError:
       stderr.print("[red]Error: invalid json format.[/]")
       raise typer.Abort()
    else:
        raw_file.close()

def execute(platform: Platform, path_to_dev_env: str) -> None:
    """ Execute the import command.
    
        Args:
            platform (Platform): The platform instance.
            path_to_dev_env (str): The path to the JSON file.
            
        Raises:
            typer.Abort: If the Development Environment already exists, or the JSON format is 
            invalid.
    """
    if os.path.exists(path_to_dev_env):
        import_dev_env_from_json(platform,path_to_dev_env)        
        platform.flush_dev_env_properties()
    else:
        stderr.print("[red]Error: The input file does not exist.[/]")