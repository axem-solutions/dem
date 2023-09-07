# Contributing

Although we don't have a contribution guideline yet, you are already welcome to participate if 
you'd like to. We want contribution to be fun, enjoyable, and educational for anyone and everyone. 
All contributions are welcome, including new features, bug fixes, new docs, blog posts, workshops, 
and more.  
You can reach out to us at [Discussions](https://github.com/axem-solutions/dem/discussions), or with 
a direct message.

## Working with the DEM source

You can use DEM as a python module. To do this, you need to add the `-m` flag to your command.

For example:

    python -m dem list --local --env

We use [poetry](https://python-poetry.org/) to manage dependencies and create a virtual environment
for DEM. To ensure that you use the correct version of the required modules, you should enter the 
preconfigured virtual environment.

First install the environment with the required dependencies:

    poetry install

Enter the virtual environment:

    poetry shell

## Running Unit Tests

Run unit tests:

    pytest tests

Run unit tests with coverage information as HTML:

    pytest --cov-report=html --cov=dem tests/

If you' like the coverate results right in your terminal:

    pytest --cov-report term-missing --cov=dem tests/