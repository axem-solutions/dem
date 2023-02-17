"""This module provides the CLI."""
# dem/cli/main.py

import typer
from dem import __app_name__, __version__

import dem.cli.dev_env.command_group as dev_env_command_group

typer_cli = typer.Typer()
typer_cli.add_typer(dev_env_command_group.typer_cli, name="dev_env")

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