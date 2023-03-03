"""This module provides the CLI."""
# dem/cli/main.py

import typer
from dem import __app_name__, __version__

from dem.cli.command import info_command, list_command

typer_cli = typer.Typer()

@typer_cli.command()
def list(local: bool = typer.Option(False, help="Scope is the local host."),
         env: bool = typer.Option(False, help="List the environments.")) -> None:
    list_command.execute(local, env)

@typer_cli.command()
def info(dev_env_name: str) -> None:
    info_command.execute(dev_env_name)

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@typer_cli.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the dem version.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return