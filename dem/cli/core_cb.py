"""The core can print information through this module."""
# dem/cli/core_cb.py

from dem.cli.console import stdout
import typer

def core_cb(*args, **kwargs):
    """ This function can be called by a core module to provide information for the user.
    
    Args:
        args -- the function acts as a class method, so it gets the caller objects as input
        kwargs -- msg: message to print
                  user_confirm: user needs to confirm an action
    """
    if "msg" in kwargs:
        stdout.print(kwargs["msg"])

    if "user_confirm" in kwargs:
        typer.confirm(kwargs["user_confirm"], abort=True)