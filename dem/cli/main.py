"""This module provides the CLI."""
# dem/cli/main.py

import typer
from dem import __app_name__, __version__

from dem.cli.command import info_cmd, list_cmd, pull_cmd

typer_cli = typer.Typer()

@typer_cli.command()
def list(local: bool = typer.Option(False, help="Scope is the local host."),
         all: bool = typer.Option(False, help="Scope is the organization."),
         env: bool = typer.Option(False, help="List the environments.")) -> None:
    """
    List the available Development Environments available locally or for the organization.
    
    The following option combinations suppported:

        --local --env -> List the local Development Environments.

        --all --env -> List the organization's Development Environments.
    """
    list_cmd.execute(local, all, env)

@typer_cli.command()
def info(dev_env_name: str = typer.Argument(...,
                                            help="Name of the Development Environment to get info about.")) -> None:
    """
    Get information about the specified Development Environment.
    """
    info_cmd.execute(dev_env_name)

@typer_cli.command()
def pull(dev_env_name: str = typer.Argument(..., 
                                            help="Name of the Development Environment to install.")) -> None:
    """
    Pull all the required containerized tools from the registry and install the Development 
    Environment locally.
    """
    pull_cmd.execute(dev_env_name)

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
    )) -> None:
    """
    Development Environment Manager (dem)
    
    Manage your containerized development environments with ease.
    """
    return