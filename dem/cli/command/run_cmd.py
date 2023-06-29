"""run CLI command implementation."""
# dem/cli/command/run_cmd.py

from dem.core.dev_env_setup import DevEnvLocalSetup
from dem.cli.console import stdout, stderr
import typer

def execute(dev_env_name: str, tool_type: str, command: str ):
    dev_env_local_setup = DevEnvLocalSetup()
    dev_env = dev_env_local_setup.get_dev_env_by_name(dev_env_name)

    if dev_env is None:
        stderr.print("[red]Error: Unknown Development Environment: " + dev_env_name + "[/]")
        raise(typer.Abort)
    else:
        dev_env.check_image_availability