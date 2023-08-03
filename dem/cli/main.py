"""This module provides the CLI."""
# dem/cli/main.py

import typer, importlib.metadata
from dem import __command__, __app_name__
from dem.cli.command import info_cmd, list_cmd, pull_cmd, create_cmd, modify_cmd, delete_cmd, \
                            rename_cmd, clone_cmd, run_cmd, export_cmd, load_cmd
from dem.cli.console import stdout

typer_cli = typer.Typer(rich_markup_mode="rich")

@typer_cli.command()
def list(local: bool = typer.Option(False, help="Scope is the local host."),
         all: bool = typer.Option(False, help="Scope is the organization."),
         env: bool = typer.Option(False, help="List the environments."),
         tool: bool = typer.Option(False, help="List the tool images.")) -> None:
    """
    List the Development Environments available locally or for the organization.
    
    The following option combinations are suppported:

        --local --env -> List the local Development Environments.

        --all --env -> List the organization's Development Environments.

        --local --tool -> List the local tool images.

        --all --tool -> List the tool images available in the axemsolutions registry.
    """
    list_cmd.execute(local, all, env, tool)

@typer_cli.command()
def info(dev_env_name: str = typer.Argument(...,
                                            help="Name of the Development Environment to get info about.")) -> None:
    """
    Get information about the specified Development Environment.
    """
    info_cmd.execute(dev_env_name)

@typer_cli.command()
def pull(dev_env_name: str = typer.Argument(..., 
                                            help="Name of the Development Environment to install.")) -> None:
    """
    Pull all the required tool images from the registry and install the Development Environment
    locally.
    """
    pull_cmd.execute(dev_env_name)

@typer_cli.command()
def clone(dev_env_name: str = typer.Argument(...,help="Name of the Development Environment to clone."),
           new_dev_env_name: str = typer.Argument(...,help="Name of the New Development Environment.")) -> None:
    """
    Clone existing Development Environment locally.
    """
    clone_cmd.execute(dev_env_name,new_dev_env_name)

@typer_cli.command()
def create(dev_env_name: str = typer.Argument(..., 
                                              help="Name of the Development Environment to create."),) -> None:
    """
    Create a new Development Environment.
    """
    create_cmd.execute(dev_env_name)

@typer_cli.command()
def export(dev_env_name: str = typer.Argument(...,help="Name of the Development Environment to export."),
           path_to_export: str = typer.Argument(None,help="Path where to extract the Dev Env.")) -> None:
    """
    Export the Development Environment.
    """
    export_cmd.execute(dev_env_name,path_to_export)    

@typer_cli.command()
def load(path_to_dev_env: str = typer.Argument(...,help="Path to load Dev Env to load.")) -> None:
    """
    Load Development Environment.
    """
    load_cmd.execute(path_to_dev_env)   

@typer_cli.command()
def rename(dev_env_name: str = typer.Argument(...,help="Name of the Development Environment to rename."),
           new_dev_env_name: str = typer.Argument(...,help="The new name.")) -> None:
    """
    Rename the Development Environment.
    """
    rename_cmd.execute(dev_env_name,new_dev_env_name)

@typer_cli.command()
def modify(dev_env_name: str = typer.Argument(..., 
                                              help="Name of the Development Environment to modify.")) -> None:
    """
    Modify the tool types and required tool images for an existing Development Environment.
    """
    modify_cmd.execute(dev_env_name)

@typer_cli.command()
def delete(dev_env_name: str = typer.Argument(..., 
                                              help="Name of the Development Environment to delete.")) -> None:
    """
    Delete the Development Environment from the local setup. If a tool image is not required
    anymore by any of the available local Development Environments, the DEM asks the user whether
    they want to delete that image or not.
    """
    delete_cmd.execute(dev_env_name)

@typer_cli.command()
def run(dev_env_name: str = typer.Argument(..., help="Name of the Development Environment"),
        tool_type: str = typer.Argument(..., help="Tool type to run."),
        workspace_path: str = typer.Argument(..., help="Workspace path."),
        command: str = typer.Argument(..., help="Command to be passed to the assigned tool image."),
        privileged: bool = typer.Option(False, help="Give extended priviliges to the container.")) -> None:
    """
    Run the image assigned to the tool type with the given command.

    :warning: Current restriction: put all parameters into quotes(")
    """
    run_cmd.execute(dev_env_name, tool_type, workspace_path, command, privileged)

def _version_callback(value: bool) -> None:
    if value:
        try: 
            version = importlib.metadata.version(__app_name__)
        except importlib.metadata.PackageNotFoundError:
            stdout.print("[yellow]Install DEM to get the version number.[/]")
        else: 
            stdout.print("[cyan]" + __app_name__ + " v" + version + "[/]")

        raise typer.Exit()

@typer_cli.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the dem version.",
        callback=_version_callback,
        is_eager=True,
    )) -> None:
    """
    Development Environment Manager (dem)
    
    Manage your containerized Development Environments with ease.



    ❗ Always put the input text into double quotation marks (""), if it contains whitespaces.

    """
    return