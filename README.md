# Manage your containerized Development Environments with ease

## Overview
The DEM is a command line tool that provides an easy, reproduceable and scalable way to set up 
Development Environments for embedded software development.

## Useful
### [Documentation](https://www.axemsolutions.io/dem_doc/index.html)
### Tutorial - coming soon

## Prerequisites

To be able to use the DEM on your PC, you need to have the following software installed:

- Python 3.10+
- Docker Engine

:information_source: Currently only the Linux operating system is supported.

## Installation

DEM is available in the PyPI repository. Install it with:

    pip install axem-dem

:information_source: The package name is axem-dem, but the command is `dem`.

## Source

You can use DEM as a python module. To do this, you need to add the `-m` flag to your command.

For example:

    python -m dem list --local --env

We use [poetry](https://python-poetry.org/) to manage dependencies. To ensure that you use the 
correct version of the required modules, you should enter the preconfigured virtual environment.

First install the environment with the required dependencies:

    poetry install

Enter the virtual environment:

    poetry shell