"""Entry point for dem."""
# dem/__main__.py

from dem import __app_name__
from dem.cli.console import stdout
import dem.cli.main 

def main():
    dem.cli.main.dem_typer_cli(prog_name=__app_name__)

if __name__ == "__main__":
    try:
        main()
    except LookupError as e:
        stdout.print("[red]" + str(e) + "[/]")