"""The core can print information through this module."""
# dem/cli/core_cb.py

from dem.cli.console import stdout
import typer

def core_cb(*args, **kwargs):
    if "msg" in kwargs:
        stdout.print(kwargs["msg"])

    if "user_confirm" in kwargs:
        typer.confirm(kwargs["user_confirm"], abort=True)