# Development Environment Manager - dem

## Overview
The dem's purpose is to have an easy, reproduceable and scalable way to set up development environments for embedded software development.

:construction: dem is under heavy development and only works with restricted functionality! :construction:

## Prerequisites:
- Please note that currently only linux is supported.
- Python:
  version >3.10 and the following python libs are required: 
  * python -m pip install rich 
  * python -m pip install typer 
  * python -m pip install docker 
  * python -m pip install pytest 
  * python -m pip install mock 
  * python -m pip install unittest 
  * python -m pip install python-dxf
- docker

 Copy the dev_env.json file from the example_json dir to ~/.config/axem directory.
 
 ## Usage
 Currently the following commands supported:
 
 `dem list [OPTIONS]`
 
 List the available Development Environments locally or for the organization.
 
 Options:
 --local Scope is the local host.
 --all Scope is the organization.
 --env List the environments.
 
 `dem info DEV_ENV_NAME`
 
 DEV_ENV_NAME: Name of the development environment.
 
 Prints out generic information about a Development Environment.
 
 `dem pull DEV_ENV_NAME`
 
 DEV_ENV_NAME: Name of the development environment to install.
 
 Installs the Development Environment by pulling the required tool container images.
