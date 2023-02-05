"""This module provides the CLI."""
# dem/main.py

from typing import Optional
import typer
from dem import __app_name__, __version__
import dem.cli.list_command as list_command
import dem.cli.info_command as info_command

dem_typer_cli = typer.Typer()

@dem_typer_cli.command()
def list() -> None:
    list_command.execute()

@dem_typer_cli.command()
def info() -> None:
    print("cicaaa")
    info_command.execute()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@dem_typer_cli.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the dem version.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return