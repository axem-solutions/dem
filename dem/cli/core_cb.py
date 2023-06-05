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

def msg_cb(*args, msg: str, rule: bool = False):
    if rule is True:
        stdout.rule(msg)
    else:
        stdout.print(msg)

def user_confirm_cb(*args, **kwargs):
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

def pull_progress_cb(*args, generator: typing.Generator):
    with Progress(TextColumn("[progress.layer_id]{task.fields[id]}"), 
                  TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TaskProgressColumn(), console=stdout) as progress:
        tasks = {}

        for item in generator:
            status = get_value_by_key_if_exist(item, ["status"])
            id = get_value_by_key_if_exist(item, ["id"])
            if status:
                if id:
                    if get_value_by_key_if_exist(item, ["progressDetail"]):
                        task = get_value_by_key_if_exist(tasks, [id])
                        if task is None:
                            task = progress.add_task(str(id), id=id)
                            tasks[id] = task

                        current = get_value_by_key_if_exist(item, ["progressDetail", "current"])
                        total = get_value_by_key_if_exist(item, ["progressDetail", "total"])

                        if current and total:
                            progress.update(task, description=str(status), total=float(total), 
                                            completed=float(current))

                    else:
                        progress.console.print(str(id) + ": " + str(status))
                else:
                    progress.console.print(str(status))