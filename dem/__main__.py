"""Entry point for dem."""
# dem/__main__.py

from dem import __command__
from dem.cli.console import stderr, stdout
from dem.core.exceptions import RegistryError
import dem.cli.main 
import docker.errors

def main():
    try:
        dem.cli.main.typer_cli(prog_name=__command__)
    except LookupError as e:
        stderr.print("[red]" + str(e) + "[/]")
    except RegistryError as e:
        stderr.print("[red]" + str(e) + "[/]")
    except docker.errors.DockerException as e:
        stderr.print("[red]" + str(e) + "[/]")

        if "Permission denied" in str(e):
            stdout.print("\nHint: Is your user part of the docker group?")
        else:
            stdout.print("\nHint: Reinstall the Docker Engine.")

# Call the main() when run as `python -m`
if __name__ == "__main__":
    main()