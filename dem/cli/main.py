"""This module provides the CLI."""
# dem/cli/main.py

import typer, importlib.metadata
from typing import Generator
from typing_extensions import Annotated
from dem import __command__, __app_name__
from dem.cli.command import cp_cmd, info_cmd, list_cmd, pull_cmd, create_cmd, modify_cmd, delete_cmd, \
                            rename_cmd, run_cmd, export_cmd, load_cmd, clone_cmd, add_reg_cmd, \
                            list_reg_cmd, del_reg_cmd, add_cat_cmd, list_cat_cmd, del_cat_cmd, \
                            add_host_cmd, uninstall_cmd
from dem.cli.console import stdout
from dem.core.platform import DevEnvLocalSetup
from dem.core.exceptions import InternalError

typer_cli: typer.Typer = typer.Typer(rich_markup_mode="rich")
platform: DevEnvLocalSetup | None = None

# Autocomplete functions
def autocomplete_dev_env_name(incomplete: str) -> Generator:
    """ 
    Autocomplete the input Dev Env name with the available matching local Dev Envs.

    Return with the matching Dev Env names by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    for dev_env in platform.local_dev_envs:
        if dev_env.name.startswith(incomplete) or (incomplete == ""):
            yield dev_env.name

def autocomplete_cat_name(incomplete: str) -> Generator:
    """ 
    Autocomplete the input Catalog name with the available matching catalogs.

    Return with the matching Catalog name by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    for catalog_config in platform.dev_env_catalogs.list_catalog_configs():
        if catalog_config["name"].startswith(incomplete) or (incomplete == ""):
            yield catalog_config["name"]

def autocomplete_reg_name(incomplete: str) -> Generator:
    """ 
    Autocomplete the input Registry name with the available matching Registries.

    Return with the matching Registry name by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    for registry_config in platform.registries.list_registry_configs():
        if registry_config["name"].startswith(incomplete) or (incomplete == ""):
            yield registry_config["name"]

# DEM commands
@typer_cli.command("list") # "list" is a Python keyword
def list_(local: Annotated[bool, typer.Option(help="Scope is the local host.")] = False,
          all: Annotated[bool, typer.Option(help="Scope is the organization.")] = False,
          env: Annotated[bool, typer.Option(help="List the environments.")] = False,
          tool: Annotated[bool, typer.Option(help="List the tool images.")] = False) -> None:
    """
    List the Development Environments available locally or for the organization.
    
    The following option combinations are suppported:

        --local --env -> List the local Development Environments.

        --all --env -> List the organization's Development Environments.

        --local --tool -> List the local tool images.

        --all --tool -> List the tool images available in the axemsolutions registry.
    """
    if platform:
        list_cmd.execute(platform, local, all, env, tool)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def info(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to get info about.",
                                                     autocompletion=autocomplete_dev_env_name)]) -> None:
    """
    Get information about the specified Development Environment available locally or in the catalogs.

    Note: Autocomplete only works with the locally avialable Dev Envs.
    """
    if platform:
        info_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def pull(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to install.")]) -> None:
    """
    Pull all the required tool images from the registry and install the Development Environment
    locally.
    """
    if platform:
        pull_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def cp(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to cp.",
                                                   autocompletion=autocomplete_dev_env_name)],
       new_dev_env_name: Annotated[str, typer.Argument(help="Name of the New Development Environment.")]) -> None:
    """
    Create a copy of a local Dev Env.
    """
    if platform:
        cp_cmd.execute(platform, dev_env_name, new_dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def create(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to create.")]) -> None:
    """
    Create a new Development Environment.
    """
    if platform:
        create_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def export(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to export.",
                                                       autocompletion=autocomplete_dev_env_name)],
           path_to_export: Annotated[str, typer.Argument(help="Path where to extract the Dev Env.")] = "") -> None:
    """
    Export the Development Environment.
    """
    if platform:
        export_cmd.execute(platform, dev_env_name,path_to_export)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def load(path_to_dev_env: Annotated[str, typer.Argument(help="Path to the Dev Env to import.")]) -> None:
    """
    Import the Development Environment.
    """
    if platform:
        load_cmd.execute(platform, path_to_dev_env)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def clone(dev_env_name: Annotated[str, typer.Argument(help="Name of the Dev Env to clone.")]) -> None:
    """
    Copy the Dev Env's descriptor from the catalog to the local descriptor storage.
    """
    if platform:
        clone_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def rename(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to rename.",
                                                       autocompletion=autocomplete_dev_env_name)],
           new_dev_env_name: Annotated[str, typer.Argument(help="The new name.")]) -> None:
    """
    Rename the Development Environment.
    """
    if platform:
        rename_cmd.execute(platform, dev_env_name,new_dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def modify(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to modify.",
                                                       autocompletion=autocomplete_dev_env_name)]) -> None:
    """
    Modify the tool types and required tool images for an existing Development Environment.
    """
    if platform:
        modify_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def delete(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to delete.",
                                                       autocompletion=autocomplete_dev_env_name)]) -> None:
    """
    Delete the Development Environment from the local setup. If a tool image is not required
    anymore by any of the available local Development Environments, the DEM asks the user whether
    they want to delete that image or not.
    """
    if platform:
        delete_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def uninstall(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to uninstall.",
                                                       autocompletion=autocomplete_dev_env_name)]) -> None:
    """
    Uninstall the Development Environment from the local setup. If a tool image is not required
    anymore by any of the available local Development Environments, the DEM will delete it.
    """
    if platform is not None:
        uninstall_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")  

@typer_cli.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(dev_env_name: Annotated[str, typer.Argument(help="Run the container in this Development Environment context",
                                                    autocompletion=autocomplete_dev_env_name)],
        ctx: Annotated[typer.Context, typer.Option()]) -> None:
    """
    Run the `docker run` command in the Development Environment's context with the given parameters.  

    This command can be used as the docker CLI one, except as first argument the name of the 
    Development Environment must be set. 
    Example: dem run dev_env --name test test_image_name:latest ls -la

    See the documentation for the list of currently supported docker run parameters.
    """
    if platform:
        run_cmd.execute(platform, dev_env_name, ctx.args)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def add_reg(name: Annotated[str, typer.Argument(help="Name of the registry to add")], 
            url: Annotated[str, typer.Argument(help="API URL of the registry")]) -> None:
    """
    Add a new registry.

    The name of the registry is what you would normally use to pull an image. 
    Examples:
        - If the full image tag: repository/image:tag -> the name should be repository.
        - If the full image tag: 192.168.1.1:5000/image:tag -> the name should be 192.168.1.1:5000

    The URL should point to the registry's REST API. For the Docker Hub its 
    https://registry.hub.docker.com, or it can be http://localhost:5000 for a self-hosted one.
    """
    if platform:
        add_reg_cmd.execute(platform, name, url)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def list_reg() -> None:
    """
    List the available registries.
    """
    if platform:
        list_reg_cmd.execute(platform)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def del_reg(registry_name: Annotated[str, typer.Argument(help="Name or IP address of the registry to delete.",
                                                         autocompletion=autocomplete_reg_name)]) -> None:
    """
    Delete a registry.
    """
    if platform:
        del_reg_cmd.execute(platform, registry_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def add_cat(name: Annotated[str, typer.Argument(help="Name of the Development Environment Catalog to add")], 
            url: Annotated[str, typer.Argument(help="URL of the Development Environment Catalog's JSON file")]) -> None:
    """
    Add a new catalog.

    You can name the catalog as you wish. 
    
    The URL must point to an HTTP(S) server where the Catalog json file is available.
    """
    if platform:
        add_cat_cmd.execute(platform, name, url)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def list_cat() -> None:
    """
    List the available catalogs.
    """
    if platform:
        list_cat_cmd.execute(platform)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def del_cat(catalog_name: Annotated[str, typer.Argument(help="Name of the Development Environment Catalog to delete.",
                                                        autocompletion=autocomplete_cat_name)]) -> None:
    """
    Delete a catalog.
    """
    if platform:
        del_cat_cmd.execute(platform, catalog_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def add_host(name: Annotated[str, typer.Argument(help="Name of the host")],
             address: Annotated[str, typer.Argument(help="IP or hostname of the host")]) -> None:
    """
    Add a new host.
    """
    if platform:
        add_host_cmd.execute(platform, name, address)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

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
