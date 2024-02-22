## Prerequisites

To use the DEM on your PC, you need to have the following tools installed:

- Python 3.10+
- Docker Engine 24.0+

!!! info

    Currently only the Linux operating system and the Docker Container Engine is supported.

## Installation

Use the following install script to get the latest version of DEM:  

    `curl -fsSL 'https://raw.githubusercontent.com/axem-solutions/dem/main/install-dem.sh' | bash`

### Alternative installation

If all the prerequisites are fulfilled, the DEM can be installed from the 
[PyPI repository](https://pypi.org/project/axem-dem/):

    pip install axem-dem

:information_source: The package name is axem-dem, but the command is `dem`.

### Enable autocompletion

After installation, you can enable the autocompletion for bash and zsh shells

    dem --install-completion

> If the command didn't work, supply your shell type as input parameter (bash or zsh)  
> Note for zsh users: `compinit` must be called from your .zshrc.

## Optional: Use the source code (for DEM developers)

The DEM can be run as a Python module. To do this, you need to add the `-m` flag to your command.

For example:

    python -m dem list --local --env

We use [poetry](https://python-poetry.org/) to manage dependencies. To ensure that you use the 
correct versions of the required modules, you should enter the preconfigured virtual environment.

First install the environment with required dependencies:

    poetry install

Enter the virtual environment:

    poetry shell

Inside the virtual environment, you can run the DEM the same way as it was an installed package:

    dem list --local --env