"""Entry point for dem."""
# dem/__main__.py

from dem import __app_name__
import dem.cli.main 

def main():
	dem.cli.main.dem_typer_cli(prog_name=__app_name__)

if __name__ == "__main__":
	main()