"""uninstall CLI command implementation."""
# dem/cli/command/uninstall_cmd.py

from dem.core.dev_env import DevEnv
from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stderr, stdout


def try_to_uninstall_dev_env(dev_env_to_uninstall: DevEnv, is_dev_env_installed: str, platform: DevEnvLocalSetup) -> bool:    
    if is_dev_env_installed == "True":                
        return platform.try_to_remove_tool_images(dev_env_to_uninstall)
    else:                
        return False        


def execute(platform: DevEnvLocalSetup, dev_env_name: str) -> None:    
    dev_env_to_uninstall = platform.get_dev_env_by_name(dev_env_name)
    is_dev_env_installed = platform.get_dev_env_status_by_name(dev_env_name)   


    if dev_env_to_uninstall is None:
        stderr.print("[red]Error: The [bold]" + dev_env_name + "[/bold] Development Environment doesn't exist.")
    else:        
        if True == try_to_uninstall_dev_env(dev_env_to_uninstall,is_dev_env_installed,platform):        
            stdout.print("[green]Successfully deleted the " + dev_env_name + "![/]")
            platform.update_dev_env_status_in_json(dev_env_to_uninstall)

        else:            
            stderr.print("[red]Error: The [bold]" + dev_env_name + "[/bold] Development Environment uninstall failed")