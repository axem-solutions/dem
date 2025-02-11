"""run CLI command implementation."""
# dem/cli/command/run_cmd.py

from dem.core.dev_env import DevEnv
from dem.core.platform import Platform
from dem.core.task import Task
from dem.cli.console import stdout, stderr
import typer

def dev_env_health_check(platform: Platform, dev_env: DevEnv) -> None:
    """ Check a Development Environment's tool images status and reinstall them if needed.
    
        Args:
            platform -- the Platform
            dev_env -- the Development Environment

        Raises:
            typer.Abort -- if the Development Environment has missing tool images
    """
    dev_env.assign_tool_image_instances(platform.tool_images)

    if not dev_env.is_installation_correct():
        stderr.print("[red]Error: Incorrect installation![/]")
        typer.confirm("Should DEM reinstall the DevEnv?", abort=True)
        platform.install_dev_env(dev_env)
        stdout.print(f"[green]DEM successfully fixed the {dev_env.name} Development Environment![/]")

def execute(platform: Platform, dev_env_name: str, task_name: str, cmd_extra_args: str) -> None:
    """ Run a task.
    
        Args:
            platform -- the Platform
            dev_env_name -- the Development Environment name
            task_name -- the task name
            cmd_extra_args -- the extra arguments for the command

        Raises:
            typer.Abort -- if the Development Environment has missing tool images
    """
    if not dev_env_name:
        if platform.default_dev_env_name:
            dev_env_name = platform.default_dev_env_name
        else:
            stderr.print("[red]Error: Only one parameter is supplied but no default Dev Env is set! Please specify the Dev Env to run the task in or set a default one![/]")
            return

    dev_env: DevEnv | None = platform.get_dev_env_by_name(dev_env_name)
    if dev_env is None:
        stderr.print("[red]Error: Unknown Development Environment: " + dev_env_name + "[/]")
        return
    
    if not dev_env.is_installed:
        stderr.print(f"[red]Error: Development Environment [bold]{dev_env_name}[/bold] is not installed![/]")
        return

    dev_env.start_engines()
    dev_env_health_check(platform, dev_env)

    task: Task | None = dev_env.tasks.get(task_name, None)

    if task:
        stdout.print(f"[green]Running task [bold]{task_name}[/bold] in Development Environment [bold]{dev_env_name}[/bold] on host {task.host_name}...[/]\n")  
        task.run()
    else:
        stderr.print(f"[red]Error: Task [bold]{task_name}[/bold] not found in Development Environment [bold]{dev_env_name}[/bold]![/]")