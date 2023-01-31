# tests/test_dem.py

from typer.testing import CliRunner
from dem import __app_name__, __version__, cli

runner = CliRunner()

def test_version():
	result = runner.invoke(cli.typer_app, ["--version"])
	assert result.exit_code == 0
	assert f"{__app_name__} v{__version__}\n" in result.stdout