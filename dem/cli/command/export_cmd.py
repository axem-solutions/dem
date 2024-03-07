"""export CLI command implementation."""
# dem/cli/command/export_cmd.py


import os
from dem.core.platform import Platform
from dem.core.dev_env import DevEnv
from dem.cli.console import stderr

def export(dev_env: DevEnv, export_path: str):
    if os.path.isdir(export_path):
        export_path = f"{export_path}/{dev_env.name}"
    elif "" == export_path:
        export_path = dev_env.name
    
    if not export_path.endswith(".json"):
        export_path += ".json"

    dev_env.export(export_path)

def execute(platform: Platform, dev_env_name: str, export_path: str) -> None:
    dev_env = platform.get_dev_env_by_name(dev_env_name)
    if dev_env:
        try:
            export(dev_env, export_path)
        except FileNotFoundError:
            stderr.print("[red]Error: Invalid input path.[/]")
    else:
        stderr.print("[red]Error: The input Development Environment does not exist.[/]")