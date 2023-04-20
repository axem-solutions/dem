"""Entry point for dem."""
# dem/__main__.py

from dem import __app_name__
from dem.cli.console import stdout, stderr
import dem.cli.main 
from dem.core.exceptions import RegistryError

def main():
    dem.cli.main.typer_cli(prog_name=__app_name__)

if __name__ == "__main__":
    try:
        main()
    except LookupError as e:
        stderr.print("[red]" + str(e) + "[/]")
    except RegistryError as e:
        stderr.print("[red]" + str(e) + "[/]")