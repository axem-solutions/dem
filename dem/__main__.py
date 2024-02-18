"""Entry point for dem."""
# dem/__main__.py

from dem import __command__
from dem.cli.console import stderr, stdout
from dem.core.exceptions import RegistryError, ContainerEngineError, InternalError, DataStorageError
import dem.cli.main
from dem.core.core import Core
from dem.core.platform import Platform
from dem.cli.tui.tui_user_output import TUIUserOutput
import docker.errors
import typer

def main() -> None:
    """ Entry point for the CLI application"""

    # Create the Development Platform
    dem.cli.main.platform = Platform()

    # Connect the UI to the user output interface
    Core.set_user_output(TUIUserOutput())

    try:
        # Load the configuration file
        dem.cli.main.platform.config_file.update()

        # Load the Dev Envs
        dem.cli.main.platform.load_dev_envs()

        # Run the CLI application
        dem.cli.main.typer_cli(prog_name=__command__)
    except LookupError as e:
        stderr.print("[red]" + str(e) + "[/]")
    except RegistryError as e:
        stderr.print("[red]" + str(e) + "\nUsing local tool images only![/]")
    except docker.errors.DockerException as e:
        stderr.print("[red]" + str(e) + "[/]")

        if "Permission denied" in str(e):
            stdout.print("\nHint: Is your user part of the docker group?")
        elif "invalid reference format" in str(e):
            stdout.print("\nHint: The input repository might not exist in the registry.")
        elif "400" in str(e):
            stdout.print("\nHint: The input parameters might not be valid.")
    except (ContainerEngineError, InternalError) as e:
        stderr.print("[red]" + str(e) + "[/]")
    except DataStorageError as e:
        stderr.print("[red]" + str(e) + "[/]")
        if typer.confirm("Do you want to reset the file?"):
            if "config.json" in str(e):
                stdout.print("Restoring the original configuration file...")
                dem.cli.main.platform.config_file.restore()
            elif "dev_env.json" in str(e):
                stdout.print("Restoring the original Dev Env descriptor file...")
                dem.cli.main.platform.dev_env_json.restore()

# Call the main() when run as `python -m`
if __name__ == "__main__":
    main()
