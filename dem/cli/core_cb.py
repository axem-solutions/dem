"""The core can provide information through this module to the user."""
# dem/cli/core_cb.py

from dem.cli.console import stdout
import typer, typing
from rich.progress import Progress, TaskID, TextColumn, BarColumn, TaskProgressColumn


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

def update_progress_bar(tasks: dict, id: str, progress: Progress, item: dict, status: str) -> None:
    """ Update the progress bar of the image pull.
    
    Args:
        tasks -- dictionary of tasks (task represent a row in the Progress table, which contains the
                 progress bar)
        id -- layer id
        progress -- contains the progress bars
        item -- current item from the generator
        status -- which process's status the progress bar shows
    """
    task = get_value_by_key_if_exist(tasks, [id])

    if task is None:
        task = progress.add_task(str(id), id=id)
        tasks[id] = task

    current = get_value_by_key_if_exist(item, ["progressDetail", "current"])
    total = get_value_by_key_if_exist(item, ["progressDetail", "total"])

    if current and total:
        progress.update(task, description=str(status), total=float(total), completed=float(current))

def process_generator_item(item: dict, tasks: dict, progress: Progress) -> None:
    """ Process an item from the generator provided by the pull command.
    
    Args:
        item-- current item from the generator
        tasks -- dictionary of tasks
        progress -- contains the progress bars
        """
    status = get_value_by_key_if_exist(item, ["status"])
    id = get_value_by_key_if_exist(item, ["id"])

    if status:
        if id:
            if get_value_by_key_if_exist(item, ["progressDetail"]):
                update_progress_bar(tasks, id, progress, item, status)
            else:
                progress.console.print(str(id) + ": " + str(status))
        else:
            progress.console.print(str(status))

def pull_progress_cb(*args, generator: typing.Generator) -> None:
    """ Process the pull command's generator

    Args:
        args -- (not used) the function acts as a class method, so it gets the caller objects as 
                input
        generator -- the pull command's generator
    """
    with Progress(TextColumn("[progress.layer_id]{task.fields[id]}"), 
                  TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TaskProgressColumn(), console=stdout) as progress:
        tasks = {}

        for item in generator:
            process_generator_item(item, tasks, progress)