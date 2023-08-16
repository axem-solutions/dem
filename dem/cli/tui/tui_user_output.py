"""The core can provide information through this module to the user."""
# dem/cli/tui/tui_user_output.py

from dem.cli.console import stdout
from dem.core.user_output import UserOutput

import typer
from typing import Generator
from rich.progress import Progress, TaskID, TextColumn, BarColumn, TaskProgressColumn
from rich.status import Status

class PullProgressBar():
    """ Visualize the status of the pull command on a progress bar."""
    def __init__(self, generator: Generator) -> None:
        """ Init the class
        
            Args:
                generator -- the status of the pull command is presented through this generator
        """
        self.tasks = {}
        self.generator = generator

    def _update_progress_bar(self, id: str, item: dict, status: str) -> None:
        """ Update the progress bar of the image pull.
        
            Args:
                id -- layer id
                item -- current item from the generator
                status -- which process's status the progress bar shows
        """
        task = self.tasks.get(id)

        if task is None:
            task = self.progress.add_task(str(id), id=id)
            self.tasks[id] = task

        progress_detail = item.get("progressDetail")
        current = None
        total = None
        if progress_detail:
            current = progress_detail.get("current")
            total = progress_detail.get("total")

        if current and total:
            self.progress.update(task, description=str(status), total=float(total), 
                                 completed=float(current))

    def _process(self, item: dict) -> None:
        """ Process an item from the generator provided by the pull command.
        
        Args:
            item-- current item from the generator
            """
        status = item.get("status")
        id = item.get("id")

        if status:
            if id:
                if item.get("progressDetail"):
                    self._update_progress_bar(id, item, status)
                else:
                    self.progress.console.print(str(id) + ": " + str(status))
            else:
                self.progress.console.print(str(status))

    def run_generator(self):
        with Progress(TextColumn("[progress.layer_id]{task.fields[id]}"), 
                      TextColumn("[progress.description]{task.description}"),
                      BarColumn(), TaskProgressColumn(), console=stdout) as self.progress:

            for item in self.generator:
                self._process(item)

class TUIUserOutput(UserOutput):

    def msg(self, text: str, is_title: bool = False) -> None:
        """ Generic callback function to present information for the user. 
        
        Args:
            msg -- the text to print
            is_title -- the text is the title of the new section.
        """
        if is_title is True:
            stdout.rule(text)
        else:
            stdout.print(text)

    def get_confirm(self, text: str, confirm_text: str) -> None:
        """ Callback function to get confirmation from the user
        
        Args:
            args -- (not used) the function acts as a class method, so it gets the caller objects as 
                    input
            kwargs -- msg: message to print
                    user_confirm: the action the user needs to confirm
        """
        if text != "":
            stdout.print(text)

        typer.confirm(confirm_text, abort=True)

    def progress_generator(self, generator: Generator) -> None:
        """ Process the pull command's generator

        Args:
            args -- (not used) the function acts as a class method, so it gets the caller objects as 
                    input
            generator -- the pull command's generator
        """
        pull_progress_bar = PullProgressBar(generator)
        pull_progress_bar.run_generator()

    def status_generator(self, generator: Generator) -> None:
        with Status("") as status:
            status.start()

            for item in generator:
                status.update(item)

            status.stop()