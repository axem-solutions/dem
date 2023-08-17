"""rename CLI command implementation."""
# dem/cli/command/rename_cmd.py

from dem.core.dev_env_setup import DevEnvLocalSetup
from dem.cli.console import stderr

def execute(dev_env_name_to_rename: str, new_dev_env_name: str) -> None:
    dev_env_local_setup = DevEnvLocalSetup()
    dev_env_to_rename = dev_env_local_setup.get_dev_env_by_name(dev_env_name_to_rename)

    if dev_env_to_rename is not None:
        dev_env_to_rename.name = new_dev_env_name
        dev_env_local_setup.flush_to_file()
    else:
        stderr.print("[red]Error: The input Development Environment does not exist.[/]")