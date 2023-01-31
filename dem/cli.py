"""This module provides the CLI."""
# dem/cli.py

from typing import Optional
import typer
from dem import __app_name__, __version__, dev_env_setup
import os
import json
from pathlib import Path

typer_app = typer.Typer()

@typer_app.command()
def list():
	#Get the raw json file.
	dev_env_json_path = Path(os.path.expanduser('~') + "/.config/axem/dev_env.json")
	dev_env_json = open(dev_env_json_path, "r")

	#Parse the json file.
	dev_env_json_deserialized = json.load(dev_env_json)

	dev_env_setup_instance = dev_env_setup.DevEnvSetup(dev_env_json_deserialized)

	for dev_env in dev_env_setup_instance.dev_envs:
		dev_env.debug_print()

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