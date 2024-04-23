## **Prerequisites**

To use DEM on your PC, you need to have the following tools installed:

- Python 3.10+
- Docker Engine 24.0+


## **Installation**


You can download the installer script from the root of the repository:

    curl -O https://raw.githubusercontent.com/axem-solutions/dem/main/install-dem.sh

If you are happy with the content of the script, you can execute it:

    bash install-dem.sh

!!! example "Example Tutorial"

    Learn by doing! Try our [tutorial](https://www.axemsolutions.io/tutorial/index.html) 
    with a simple embedded project!


### <ins>Alternative installation</ins>

If all the prerequisites are fulfilled, DEM can be installed from the 
[PyPI repository](https://pypi.org/project/axem-dem/):

    pip install axem-dem

:information_source: The package name is axem-dem, but the command is `dem`.

### <ins>Enable autocompletion</ins>

After installation, you can enable the autocompletion for bash and zsh shells

    dem --install-completion

> If the command didn't work, supply your shell type as input parameter (bash or zsh)  
> Note for zsh users: `compinit` must be called from your .zshrc.

## **Optional: Use the source code (for DEM developers)**

DEM can be run as a Python module. To do this, you need to add the `-m` flag to your command.

For example:

    python -m dem list

We use [poetry](https://python-poetry.org/) to manage dependencies. To ensure that you use the 
correct versions of the required modules, you should enter the preconfigured virtual environment.

First install the environment with required dependencies:

    poetry install

Enter the virtual environment:

    poetry shell

Inside the virtual environment, you can run DEM the same way as it was an installed package:

    dem list