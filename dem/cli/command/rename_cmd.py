"""rename CLI command implementation."""
# dem/cli/command/rename_cmd.py

from dem.core.platform import DevEnvLocalSetup
from dem.cli.console import stderr

def execute(dev_env_name_to_rename: str, new_dev_env_name: str) -> None:
    platform = DevEnvLocalSetup()
    dev_env_to_rename = platform.get_dev_env_by_name(dev_env_name_to_rename)

    if dev_env_to_rename is not None:
        dev_env_to_rename.name = new_dev_env_name
        platform.flush_to_file()
    else:
        stderr.print("[red]Error: The input Development Environment does not exist.[/]")