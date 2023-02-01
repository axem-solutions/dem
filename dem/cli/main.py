"""This module provides the CLI."""
# dem/cli.py

from typing import Optional
import typer
from dem import __app_name__, __version__, dev_env_setup
import os
import json
from pathlib import Path
import docker
from rich.console import Console
from rich.table import Table

typer_app = typer.Typer()
console = Console()

@typer_app.command()
def list():
	#Get the raw json file.
	dev_env_json_path = Path(os.path.expanduser('~') + "/.config/axem/dev_env.json")
	dev_env_json = open(dev_env_json_path, "r")

	#Parse the json file.
	dev_env_json_deserialized = json.load(dev_env_json)
	dev_env_setup_instance = dev_env_setup.DevEnvSetup(dev_env_json_deserialized)

	client = docker.from_env()

	table = Table()
	table.add_column("Development Environment")
	table.add_column("Status")

	local_image_tags = []

	for image in client.images.list():
		for tag in image.tags:
			local_image_tags.append(tag)

	for dev_env in dev_env_setup_instance.dev_envs:
		checked_images = dev_env.validate(local_image_tags)
		if "missing" in checked_images.values():
			print_validation_result = "[red]✗ Missing images[/]"
		else:
			print_validation_result = "[green]✓[/]"
		table.add_row(dev_env.name, print_validation_result)

	console.print(table)

def _version_callback(value: bool) -> None:
	if value:
		typer.echo(f"{__app_name__} v{__version__}")
		raise typer.Exit()

@typer_app.callback()
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