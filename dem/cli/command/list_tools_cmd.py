"""list-tools command implementation."""
# dem/cli/command/list_tools_cmd.py

from dem.core.platform import Platform
from dem.core.tool_images import ToolImage
from dem.cli.console import stdout, stderr
from rich.table import Table
import typer

def list_local_tools(platform: Platform) -> None:
    """ List the local tools.
    
        Args:
            platform -- the Platform

        Exceptions:
            typer.Abort -- if no local tool images are available
    """
    if not platform.tool_images.all_tool_images:
        stdout.print("[yellow]No local tool images are available.[/]")
        raise typer.Abort()

    stdout.print(f"\n [italic]Local Tool Images[/]")
    # sorted will return a list of tuples, so we can iterate over the items
    for tool_image in sorted(platform.tool_images.all_tool_images.items()):
        # tool_image[0] is the name of the tool image and tool_image[1] is the ToolImage instance
        stdout.print(f"  {tool_image[0]}")

def update_tools_from_selected_regs(platform: Platform, selected_regs: list[str]) -> None:
    """ Update the tools from the selected registries only. 
    
        Args:
            platform -- the Platform
            selected_regs -- the selected registry names

        Exceptions:
            typer.Abort -- if an unknown registry is specified
    """
    available_regs = set([reg["name"] for reg in platform.config_file.registries])
    selected_regs = set(selected_regs)

    if not selected_regs.issubset(available_regs):
        for unkown_reg in selected_regs - available_regs:
            stderr.print(f"[red]Error: Registry {unkown_reg} is not available![/]")
        raise typer.Abort()

    platform.tool_images.update(False, True, reg_selection=selected_regs)

def list_tools_from_regs(platform: Platform, table: Table) -> None:
    """ List the available tools from the registries.
    
        Args:
            platform -- the Platform
            table -- the rich Table instance to fill with the tool image data
    """
    table.add_column("Name")
    table.add_column("Available locally?")
    # sorted will return a list of tuples, so we can iterate over the items
    for tool_image in sorted(platform.tool_images.get_registry_ones().items()):
        # tool_image[0] is the name of the tool image and tool_image[1] is the ToolImage instance
        tool_image_name = tool_image[0]
        tool_image: ToolImage = tool_image[1]
        
        if tool_image.availability == ToolImage.LOCAL_AND_REGISTRY:
            available_locally = "[green]✔[/]"
        else:
            available_locally = ""

        table.add_row(tool_image_name, available_locally)

def list_tools_from_selected_regs(platform: Platform, specified_regs: list[str]) -> None:
    """ List the available tools from the selected registries only.
    
        Args:
            platform -- the Platform
            specified_regs -- the selected registry names
            
        Exceptions:
            typer.Abort -- if no tool images are available in the selected registries
    """
    update_tools_from_selected_regs(platform, specified_regs)

    if not platform.tool_images.get_registry_ones():
        stdout.print("[yellow]No tool images are available in the selected registries.[/]")
        raise typer.Abort()

    table = Table()
    list_tools_from_regs(platform, table)
    stdout.print(f"\n [italic]Available Tool Images from the selected registries[/]")
    stdout.print(table)

def list_tools_from_all_regs(platform: Platform) -> None:
    """ List the available tools from all registries.
    
        Args:
            platform -- the Platform
        
        Exceptions:
            typer.Abort -- if no tool images are available in the registries
    """
    platform.tool_images.update(False, True)
    if not platform.tool_images.get_registry_ones():
        stdout.print("[yellow]No tool images are available in the registries.[/]")
        raise typer.Abort()

    table = Table()
    list_tools_from_regs(platform, table)
    stdout.print(f"\n [italic]Available Tool Images from all registries[/]")
    stdout.print(table)

def execute(platform: Platform, reg: bool, selected_regs: list[str]) -> None:
    """ List the available tools.
        
        Args:
            platform -- the Platform
            reg -- the flag to list the tools from the registries
            selected_regs -- the selected registry names
        
        Exceptions:
            typer.Abort -- if no tool images are available either locally or in the registries or 
                           if an unknown registry is specified
    """
    if not reg:
        list_local_tools(platform)
    elif selected_regs:
        list_tools_from_selected_regs(platform, selected_regs)
    else:
        list_tools_from_all_regs(platform)