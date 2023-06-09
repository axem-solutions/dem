"""Provide a Console intance for the CLI UI."""
# dem/cli/console.py

from rich.console import Console

stdout = Console(highlight=False)
stderr = Console(stderr=True)