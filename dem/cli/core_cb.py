"""The core can provide information through this module to the user."""
# dem/cli/core_cb.py

from dem.cli.console import stdout
import typer, typing
from rich.progress import Progress, TaskID, TextColumn, BarColumn, TaskProgressColumn


def get_value_by_key_if_exist(dictionary: dict, keys: list[str]) -> str | TaskID | None:
    for key in keys:
        try:
            dictionary = dictionary[key]
        except KeyError:
            return None

    return dictionary


def get_value_by_key_if_exist(dictionary: dict, keys: list[str]) -> str | TaskID | None:
    """ Returns with the value based on the key if it exists, None if not.
    
    Args:
        dictionary -- the dictionary to get the value from
        keys -- list of keys that addresses a nested value
    """
    for key in keys:
        try:
            dictionary = dictionary[key]
        except KeyError:
            return None

    return dictionary

def msg_cb(*args, msg: str, rule: bool = False) -> None:
    """ Generic callback function to present information for the user. 
    
    Args:
        args -- (not used) the function acts as a class method, so it gets the caller objects as 
                input
        msg -- the message to print
        rule -- indicate the start of a new section
    """
    if rule is True:
        stdout.rule(msg)
    else:
        stdout.print(msg)

def user_confirm_cb(*args, **kwargs) -> None:
    """ Callback function to get confirmation from the user
    
    Args:
        args -- (not used) the function acts as a class method, so it gets the caller objects as 
                input
        kwargs -- msg: message to print
                  user_confirm: the action the user needs to confirm
    """
    if "msg" in kwargs:
        stdout.print(kwargs["msg"])

    if "user_confirm" in kwargs:
        typer.confirm(kwargs["user_confirm"], abort=True)

def pull_progress_cb(*args, generator: typing.Generator):
    with Progress(TextColumn("[progress.layer_id]{task.fields[id]}"), 
                  TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TaskProgressColumn()) as progress:
        tasks = {}

        for item in generator:
            process_generator_item(item, tasks, progress)
