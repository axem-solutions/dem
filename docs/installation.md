## **Prerequisites**

To use DEM on your PC, you need to have the following tools installed:

- Python 3.10+
- Docker Engine 24.0+


## **Installation**

First, install Python and Docker if you haven't already:

- [Python](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/)

Make sure to include **pip** during Python installation.

Install DEM from the PyPI repository using:

    pip install axem-dem

- The package name is 'axem-dem', but the command is `dem`.
- Ensure the Docker daemon is running before using DEM.

### <ins>Enable autocompletion</ins>

After installation, you can enable the autocompletion for bash and zsh shells

    dem --install-completion

If the command doesn't work, specify your shell type as an input parameter (powershell, bash, or zsh).

> Note for zsh users: `compinit` must be called from your .zshrc.

!!! example "Example Tutorial"

    Learn by doing! Try our [tutorial](https://www.axemsolutions.io/tutorial/index.html) 
    with a simple embedded project!

## **Alternative method: run DEM from source**

To run the DEM from source, you need to clone the repository first

    git clone https://github.com/axem-solutions/dem

DEM can be run as a Python module. To do this, you need to add the `-m` flag to your command.

For example:

    python -m dem list

We use [poetry](https://python-poetry.org/) to manage dependencies. To ensure that you use the 
correct versions of the required modules, you should enter the preconfigured virtual environment.

If you don't have poetry installed, you can install it with:

    pip install poetry

First install the environment with required dependencies:

    poetry install

Enter the virtual environment:

    poetry shell

Inside the virtual environment, you can run DEM the same way as it was an installed package:

    dem list