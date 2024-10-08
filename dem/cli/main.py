"""This module provides the CLI."""
# dem/cli/main.py

import typer, importlib.metadata
from typing import Generator
from typing_extensions import Annotated
import os
from dem import __command__, __app_name__
from dem.cli.command import cp_cmd, import_cmd, info_cmd, list_cmd, create_cmd, modify_cmd, \
                            delete_cmd, rename_cmd, run_cmd, export_cmd, clone_cmd, add_reg_cmd, \
                            list_reg_cmd, del_reg_cmd, add_cat_cmd, list_cat_cmd, del_cat_cmd, \
                            add_host_cmd, set_default_cmd, uninstall_cmd, install_cmd, assign_cmd, \
                            init_cmd, list_host_cmd, del_host_cmd, list_tools_cmd, add_task_cmd, \
                            del_task_cmd
from dem.cli.console import stdout
from dem.core.platform import Platform
from dem.core.exceptions import InternalError

typer_cli: typer.Typer = typer.Typer(rich_markup_mode="rich")
platform: Platform | None = None

# Autocomplete functions
def autocomplete_dev_env_name(incomplete: str) -> Generator:
    """ 
    Autocomplete the input Dev Env name with the available matching local Dev Envs.

    Return with the matching Dev Env names by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    if platform is not None:
        for dev_env in platform.local_dev_envs:
            if dev_env.name.startswith(incomplete) or (incomplete == ""):
                yield dev_env.name

def autocomplete_installed_dev_env_name(incomplete: str) -> Generator:
    """ 
    Autocomplete the input Dev Env name with the available matching installed Dev Envs.

    Return with the matching Dev Env names by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    if platform is not None:
        for dev_env in platform.local_dev_envs:
            if dev_env.is_installed and (dev_env.name.startswith(incomplete) or (incomplete == "")):
                yield dev_env.name

def autocomplete_cat_name(incomplete: str) -> Generator:
    """ 
    Autocomplete the input Catalog name with the available matching catalogs.

    Return with the matching Catalog name by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    if platform is not None:
        for catalog in platform.dev_env_catalogs.catalogs:
            if catalog.name.startswith(incomplete) or (incomplete == ""):
                yield catalog.name

def autocomplete_reg_name(incomplete: str) -> Generator:
    """ 
    Autocomplete the input Registry name with the available matching Registries.

    Return with the matching Registry name by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    if platform is not None:
        for registry_config in platform.registries.list_registry_configs():
            if registry_config["name"].startswith(incomplete) or (incomplete == ""):
                yield registry_config["name"]

def autocomplete_host_name(incomplete: str) -> Generator:
    """ 
    Autocomplete the input Host name with the available matching Hosts.

    Return with the matching Host name by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    if platform is not None:
        for host_config in platform.hosts.list_host_configs():
            if host_config["name"].startswith(incomplete) or (incomplete == ""):
                yield host_config["name"]

def autocomplete_task_name(ctx: typer.Context, incomplete: str) -> Generator:
    """ 
    Autocomplete the input Task name with the available matching Task names.

    Return with the matching Task name by a Generator.
    
    Args:
        incomplete -- the parameter the user supplied so far when the tab was pressed
    """
    dev_env_name = ctx.params.get("dev_env_name", None)
    if platform is not None and dev_env_name is not None:
        for dev_env in platform.local_dev_envs:
            if dev_env.name == dev_env_name:
                for task_name in dev_env.tasks:
                    if task_name.startswith(incomplete) or (incomplete == ""):
                        yield task_name

# DEM commands
@typer_cli.command()
def add_task(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to add the task to.",
                                                         autocompletion=autocomplete_dev_env_name)],
             task_name: Annotated[str, typer.Argument(help="Name of the task.")], 
             command: Annotated[str, typer.Argument(help="The command the task should execute.")]) -> None:
    """
    Add a new task to the Development Environment.

    The command will be executed when the `dem run dev_env_name task_name` command is called. The 
    command must be surrounded by quotes.
    """
    if platform:
        add_task_cmd.execute(platform, dev_env_name, task_name, command)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def del_task(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to delete the task from.",
                                                         autocompletion=autocomplete_dev_env_name)],
             task_name: Annotated[str, typer.Argument(help="Name of the task to delete.",
                                                      autocompletion=autocomplete_task_name)]) -> None:
    """
    Delete a task from the Development Environment.
    """
    if platform:
        del_task_cmd.execute(platform, dev_env_name, task_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def set_default(dev_env_name: Annotated[str, 
                                     typer.Argument(help="The name of the Development Environment to set as default.",
                                                    autocompletion=autocomplete_installed_dev_env_name)]) -> None:
    """
    Set the Development Environment as the default one.

    The default Development Environment will be used by the run command when no Development 
    Environment is specified.
    """
    if platform:
        set_default_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command("list", context_settings={"allow_extra_args": True}) # "list" is a Python keyword
def list_(cat: Annotated[bool, typer.Option(help="List the Dev Envs available from the catalogs.",
                                            show_default=False)] = False,
          ctx: Annotated[typer.Context, typer.Option()] = None) -> None:
    """
    List the Dev Envs.

    By default the local Dev Envs will be listed.
    
    --cat: List the available Dev Envs from the catalogs. Specify the catalogs' name to list the Dev 
    Envs from. More then one catalog can be specified. If no catalog is specified, all the available
    catalogs will be used.
    """
    if platform and ctx:
        list_cmd.execute(platform, cat, ctx.args)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command(context_settings={"allow_extra_args": True})
def list_tools(reg: Annotated[bool, typer.Option(help="List the available tools in the registries.",
                                                  show_default=False)] = False,
               ctx: Annotated[typer.Context, typer.Option()] = None) -> None:
    """
    List the available tools.

    By default the local tools will be listed.

    --reg: List the available tools in the registries. Specify the registry's name to list the tools
    from. More then one registry can be specified. If no registry is specified, all the available
    registries will be used.
    """
    if platform and ctx:
        list_tools_cmd.execute(platform, reg, ctx.args)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command(context_settings={"allow_extra_args": True})
def info(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to get info about.",
                                                     autocompletion=autocomplete_dev_env_name)],
         cat: Annotated[bool, typer.Option(help="Get the Dev Env from the catalogs")] = False,
         ctx: Annotated[typer.Context, typer.Option()] = None) -> None:
    """
    Get information about the specified Development Environment available locally or in the catalogs.

    --cat: DEM will search for the Dev Env in the catalogs and will print the details of the first
    match. You can specifiy the catalogs' name to search in after this option. If no catalog is 
    specified, all the available catalogs will be used. If the Dev Env is not found in the catalogs,
    an error message will be printed.

    Note: Autocomplete only works with the locally avialable Dev Envs.
    """
    if platform and ctx:
        info_cmd.execute(platform, dev_env_name, cat, ctx.args)
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

@typer_cli.command("import")
def import_(path_to_dev_env: Annotated[str, typer.Argument(help="Path to the Dev Env to import.")]) -> None:
    """
    Import the Development Environment.
    """
    if platform:
        import_cmd.execute(platform, path_to_dev_env)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def clone(dev_env_name: Annotated[str, typer.Argument(help="Name of the Dev Env descriptor to clone.")]) -> None:
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
    Change a tool in a Development Environment.

    If the tool type is not specified, the Dev Env settings panel will be opened.
    """
    if platform:
        modify_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def delete(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to delete.",
                                                       autocompletion=autocomplete_dev_env_name)]) -> None:
    """
    Delete the Dev Env descriptor from the local descriptor storage.
    If the Dev Env is installed, the user will be asked whether they want to uninstall it. 
    """
    if platform:
        delete_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def install(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to install.",
                                                       autocompletion=autocomplete_dev_env_name)]) -> None:
    """
    Install the Development Environment.
    """
    if platform is not None:
        install_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")
    
@typer_cli.command()
def uninstall(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to uninstall.",
                                                       autocompletion=autocomplete_dev_env_name)]) -> None:
    """
    Uninstall the Development Environment from the local setup. If a tool image is not required
    anymore by any of the available local Development Environments, the DEM will delete it.
    """
    if platform:
        uninstall_cmd.execute(platform, dev_env_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")  

@typer_cli.command()
def assign(dev_env_name: Annotated[str, typer.Argument(help="Name of the Dev Env that should be assign to the project.",
                                                       autocompletion=autocomplete_dev_env_name)],
           project_path: Annotated[str, typer.Argument(help="Path of the project.")] = os.getcwd()) -> None:
    """
    Assign a Development Environment to a project.

    If the project path is not specified, the current working directory will be used.
    """
    if platform:
        assign_cmd.execute(platform, dev_env_name, project_path)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def init(project_path: Annotated[str, typer.Argument(help="Path of the project.")] = os.getcwd()) -> None:
    """
    Initialize the DevEnv assigned to the project.

    If the project path is not specified, the current working directory will be used.
    """
    if platform:
        init_cmd.execute(platform, project_path)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def run(dev_env_name: Annotated[str, typer.Argument(help="Name of the Development Environment to run the task in. If not set, the default Dev Env will be used.",
                                                    autocompletion=autocomplete_installed_dev_env_name)] = "",
        task_name: Annotated[str, typer.Argument(help="The name of the task to run.",
                                                 autocompletion=autocomplete_task_name)] = "") -> None:
    """
    Run the task of the Development Environment. The Dev Env must be installed.

    If the Dev Env is not specified, the default Dev Env will be used. If the default Dev Env is not
    set, an error message will be printed.
    """
    if platform:
        # If only a single parameter is supplied, we assume it's the task name
        if not task_name and dev_env_name:
            task_name = dev_env_name
            dev_env_name = ""
        run_cmd.execute(platform, dev_env_name, task_name)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def add_reg(name: Annotated[str, typer.Argument(help="Unique name for the registry")], 
            url: Annotated[str, typer.Argument(help="API URL of the registry")],
            namespace: Annotated[str, typer.Argument(help="Namespace inside the registry")] = "")-> None:
    """
    Add a new registry.

    The name of the registry must be unique.

    The namespace is only mandatory for Docker Hub registries.

    The URL should point to the registry's REST API. For the Docker Hub its 
    https://registry.hub.docker.com, or it can be http://localhost:5000 for a self-hosted one.
    """
    if platform:
        add_reg_cmd.execute(platform, name, url, namespace)
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
def del_reg(registry_name: Annotated[str, typer.Argument(help="Name of the registry to delete.",
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

@typer_cli.command()
def list_host() -> None:
    """
    List the available hosts.
    """
    if platform is not None:
        list_host_cmd.execute(platform)
    else:
        raise InternalError("Error: The platform hasn't been initialized properly!")

@typer_cli.command()
def del_host(host_name: Annotated[str, typer.Argument(help="Name of the host to delete.", 
                                                      autocompletion=autocomplete_host_name)]) -> None:
    """
    Delete a host.
    """
    if platform:
        del_host_cmd.execute(platform, host_name)
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
    """
    return
