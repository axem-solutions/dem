"""Unit tests for running the dem in CLI mode without commands."""
from dem import __app_name__, __version__
from typer.testing import CliRunner
import dem.cli.main as main

runner = CliRunner()

def test_version():
	result = runner.invoke(main.dem_typer_cli, ["--version"])

	assert result.exit_code == 0
	assert f"{__app_name__} v{__version__}\n" in result.stdout