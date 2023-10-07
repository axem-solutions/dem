"""Entry point for dem."""
# dem/__main__.py

from dem import __command__
from dem.cli.console import stderr, stdout
from dem.core.exceptions import RegistryError, ContainerEngineError
import dem.cli.main
import docker.errors
from dem.core.core import Core
from dem.cli.tui.tui_user_output import TUIUserOutput

def main():
    """ Entry point for the CLI application"""

    # Connect the UI to the user output interface
    Core.set_user_output(TUIUserOutput())

    try:
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
    except ContainerEngineError as e:
        stderr.print("[red]" + str(e) + "[/]")

# Call the main() when run as `python -m`
if __name__ == "__main__":
    main()
