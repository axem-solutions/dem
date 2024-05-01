"""add-task CLI command implementation."""
# dem/cli/command/add_task_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stderr, stdout

def execute(platform: Platform, dev_env_name: str, task_name: str, command: str) -> None:
    """ Add a task to a Development Environment.
    
        Args:
            platform -- the Platform
            dev_env_name -- the Development Environment name
            task_name -- the task name
            command -- the command
    """
    dev_env = platform.get_dev_env_by_name(dev_env_name)
    if dev_env is None:
        stderr.print(f"[red]Error: Development Environment '{dev_env_name}' not found![/]")
        return
    dev_env.add_task(task_name, command)
    platform.flush_dev_env_properties()
    stdout.print(f"[green]Task [bold]{task_name}[/bold] added to Development Environment [bold]{dev_env_name}[/bold]![/]")