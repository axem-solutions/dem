<div align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="docs/wp-content/dem_logo_dark.png">
        <img alt="DEM logo" src="docs/wp-content/dem_logo_light.png" width="150">
    </picture>
</div>

<br>

<h1 align="center">
    Development Environment Manager <br /> for <br /> Embedded Development
</h1>

<h3 align="center">
Manage your isolated Development Environments with ease
</h3>
<br />

<p align="center">
    <a href="https://github.com/axem-solutions/dem/tags" target="_blank"><img src="https://img.shields.io/github/v/tag/axem-solutions/dem?logo=github&color=79A7B5&link=https%3A%2F%2Fgithub.com%2Faxem-solutions%2Fdem%2Freleases" alt="GitHub tag (with filter)"/></a>
    <a href="https://github.com/axem-solutions/dem/issues" target="_blank"><img src="https://img.shields.io/github/issues/axem-solutions/dem?logo=github&color=2ea087&link=https%3A%2F%2Fgithub.com%2Faxem-solutions%2Fdem%2Fissues" alt="GitHub issues"/></a>
    <a href="https://discord.com/invite/Nv6hSzXruK" target="_blank"><img src="https://img.shields.io/discord/1156270239860920431?logo=discord&color=2C2F33&link=https%3A%2F%2Fdiscord.com%2Finvite%Nv6hSzXruK" alt="Discord"/></a>
</p>

<br />

<h3 align="center">
:star2: Join our Community on  <a href="https://discord.com/invite/Nv6hSzXruK">Discord</a> :star2:
</h3>

<h4 align="center">
Get answers to your challenges, and learn more about DEM, embedded development tools, and development platforms.
</h4>

<br />

## Overview

<p align="center">
<strong>
<a href="https://www.axemsolutions.io/dem_doc/index.html">Documentation</a> • <a href="https://www.axemsolutions.io/tutorial/index.html">Tutorial</a> • 
<a href="https://github.com/axem-solutions/.github/blob/4bdc1be72b0a2c97da19408c59d6dd5d1845a469/CONTRIBUTING.md">Contribution guide</a> • 
<a href="https://github.com/axem-solutions/.github/blob/4bdc1be72b0a2c97da19408c59d6dd5d1845a469/SUPPORT.md">Support</a>
</strong>
</p>

The DEM is a command line tool that provides an easy, reproducible, and scalable way to set up 
Development Environments for embedded software development.
> The DEM can be used locally, but it is in alpha state, so expect major new features!

<p align="center">
Contributors and early adopters are welcome!
</p>

## The Concept in a Nutshell
A set of software tools used for a specific development project is called a Development Environment.
These tools for example can be the build system, debugger, test framework, etc...  

The idea is to pack the tools separately into container images, which are then can be stored in 
registries.

Each Development Environment has a descriptor. A descriptor, like a blueprint, indicates which tools 
are required in the project, and the place their container images are stored.

![Dev Env descriptor](/docs/wp-content/dev_env_descriptor.png)

The descriptors can be stored in the Development Environment Catalogs. The users can browse these 
catalogs, and download a copy of the Development Environment descriptor to their local catalog.

![Catalogs](/docs/wp-content/dem_catalogs.png)

The users can install a Development Environments from their local catalog or freely create their own 
based on the tools available in the registries or on their local system.

![Dev Env installation](/docs/wp-content/dev_env_installation.png)

## Key features

- Create scalable, reliable, and reproducible containerized Development Environments
- Manage your containerized tools
- Install preconfigured Development Environments from catalogs
- Ensure that everyone in the team works with the same toolset
- Share Development Environments outside of your organization

## Prerequisites

To be able to use the DEM on your PC, you need to have the following software installed:

- Python 3.10+
- Docker Engine 24.0+

:information_source: Currently only the Linux operating system and the Docker Engine are supported.

## Installation

You can download the installer script from the root of the repository:

    curl -O https://raw.githubusercontent.com/axem-solutions/dem/main/install-dem.sh

If you are happy with the content of the script, you can execute it:

    bash install-dem.sh

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

## Quick start

We got you covered in all scenarios:

### I'd like to start with a template...

Here at axem we'd like to create a template for every target out there. List the currently available
ones with:

    dem list --all --env

You can clone the selected template with:

    dem clone DEV_ENV_NAME

### I'd like to work on a project already configured with DEM...

In this case you only need to initialize the Dev Env with:

    dem init

### I'd like to use a Dev Env someone shared with me...

You can import a Dev Env descriptor JSON with: 

    dem load PATH_TO_DEV_ENV

where PATH_TO_DEV_ENV is the path to the JSON file.

### I'd like to create my own Dev Env from scratch...

Create a brand new Dev Env with the following command:

    dem create DEV_ENV_NAME


Now you have the Dev Env descriptor in your local catalog, but you might want to set a few things:
- Add/remove tools.
- Change the tool image for a given tool.
- Set the host where the image should be placed.

You can edit it with:

    dem modify DEV_ENV_NAME

Finally, if you are ready to use the Development Environment, you can install it with:

    dem install DEV_ENV_NAME

>For more detailed instructions please refer to the
[Documentation](https://www.axemsolutions.io/dem_doc/index.html)
