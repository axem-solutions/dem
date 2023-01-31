"""Entry point for dem."""
# dem/__main__.py

from dem import cli, __app_name__

def main():
	cli.typer_app(prog_name=__app_name__)

if __name__ == "__main__":
	main()