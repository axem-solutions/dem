"""del-task CLI command implementation."""
# dem/cli/command/del_task_cmd.py

from dem.core.platform import Platform
from dem.cli.console import stderr

def execute(platform: Platform, dev_env_name: str, task_name: str) -> None:
    """ Delete a task from a Development Environment.
    
        Args:
            platform -- the Platform
            dev_env_name -- the Development Environment name
            task_name -- the task name
    """
    dev_env = platform.get_dev_env_by_name(dev_env_name)
    if dev_env is None:
        stderr.print(f"[red]Error: Development Environment '{dev_env_name}' not found![/]")
        return

    try:
        dev_env.del_task(task_name)
    except KeyError as e:
        stderr.print(f"[red] Error: {str(e)}[/]")
        return

    platform.flush_dev_env_properties()