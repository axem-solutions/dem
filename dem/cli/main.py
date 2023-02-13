"""This module provides the CLI."""
# dem/main.py

from typing import Optional
import typer
from dem import __app_name__, __version__
from typing import Optional
from rich.console import Console
from rich.table import Table
import dem.core.dev_env_setup as dev_env_setup
import docker
import dem.core.data_management as data_management

dem_typer_cli = typer.Typer()
console = Console()

def print_list_table(dev_envs: list, local_image_tags: list) -> None:
	table = Table()
	table.add_column("Development Environment")
	table.add_column("Status")

	for dev_env in dev_envs:
		checked_images = dev_env.validate(local_image_tags)
		if "missing" in checked_images.values():
			print_validation_result = "[red]✗ Missing images[/]"
		else:
			print_validation_result = "[green]✓[/]"
		table.add_row(dev_env.name, print_validation_result)

	console.print(table)


@dem_typer_cli.command()
def list() -> None:
	dev_env_json_deserialized = data_management.get_deserialized_dev_env_json()
	dev_env_setup_instance = dev_env_setup.DevEnvSetup(dev_env_json_deserialized)

	client = docker.from_env()

	local_image_tags = []

	for image in client.images.list():
		for tag in image.tags:
			local_image_tags.append(tag)

	if dev_env_setup_instance.dev_envs:
		print_list_table(dev_env_setup_instance.dev_envs, local_image_tags)
	else:
		console.print("[yellow]No installed Development Environments.[/]")


def _version_callback(value: bool) -> None:
	if value:
		typer.echo(f"{__app_name__} v{__version__}")
		raise typer.Exit()

@dem_typer_cli.callback()
def main(
	version: Optional[bool] = typer.Option(
		None,
		"--version",
		"-v",
		help="Show the dem version.",
		callback=_version_callback,
		is_eager=True,
	)
) -> None:
	return