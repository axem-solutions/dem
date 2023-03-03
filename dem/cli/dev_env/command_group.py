"""dev_env command group: manage the Dev Envs."""
# dem/cli/dev_env/command_group.py

import typer
from dem.cli.dev_env import info_command, list_command

typer_cli = typer.Typer()

@typer_cli.command()
def list() -> None:
    list_command.execute()

@typer_cli.command()
def info(dev_env_name: str) -> None:
    info_command.execute(dev_env_name)