## Prerequisites

To use the DEM on your PC, you need to have the following tools installed:

- Python 3.10+
- Docker Engine 24.0+

!!! info

    Currently only the Linux operating system and the Docker Container Engine is supported.

## Installation

dem is available in the PyPI repository. Install it with:

    pip install axem-dem

And that's it! Now you should be able to use the `dem` command.

!!! info

    The package name is axem-dem, but the command is `dem`.


You can also install it with install-dem.sh from our repository. The installer script checks if the 
corresponding python version is available and installs the docker and axem-dem pip module.
Download it with the following command:

    curl 'https://raw.githubusercontent.com/axem-solutions/dem/main/install-dem.sh' > install-dem.sh
   
Then execute it:

    ./install-dem.sh

## Optional: Use the source code

The dem is [open source](https://github.com/axem-solutions/dem), so you can use it as a python 
module. To do this, you need to add the `-m` flag to your command.

For example:

    python -m dem list --local --env

We use [poetry](https://python-poetry.org/) to manage dependencies. To ensure that you use the 
correct versions of the required modules, you should enter the preconfigured virtual environment.

First install the environment with required dependencies:

    poetry install

Enter the virtual environment:

    poetry shell