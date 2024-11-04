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

<br />

## Overview

<p align="center">
<strong>
<a href="https://www.axemsolutions.io/dem_doc/index.html">Documentation</a> • <a href="https://www.axemsolutions.io/tutorial/index.html">Tutorial</a> • 
<a href="https://github.com/axem-solutions/.github/blob/4bdc1be72b0a2c97da19408c59d6dd5d1845a469/CONTRIBUTING.md">Contribution Guide</a> • 
<a href="https://github.com/axem-solutions/.github/blob/4bdc1be72b0a2c97da19408c59d6dd5d1845a469/SUPPORT.md">Support</a>
</strong>
</p>

**DEM** is a command-line tool that provides an easy, reproducible, and scalable way to set up 
multi-container-based Development Environments (DevEnvs for short) for software development.

> DEM is currently in alpha state, so expect major changes in the future!

<p align="center">
Contributors and early adopters are welcome!
</p>

## Key features

- Create scalable, reliable, and reproducible containerized Development Environments where each tool 
is isolated in its own container.
- Install preconfigured Development Environments from catalogs.
- Ensure that everyone on your team works with the same toolset.

## How is DEM Different?
Unlike other container-based development environments that pack all tools into a single image 
requiring users to enter the container via an interactive shell, DEM creates a separate container 
for each tool. This allows you to work on your host system with your usual setup while the 
development-specific tools are isolated in containers.

## Prerequisites

Linux and Windows are supported.

:information_source: macOS is not yet officially supported. However, if all prerequisites are met, 
DEM should work on macOS as well.

DEM depends on Python and Docker. Ensure you have the following versions:

- Python 3.10+
- Docker Engine 24.0+

## Installation

First, install Python and Docker if you haven't already:

- [Python](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/)

Make sure to include **pip** during Python installation.

Install DEM from the PyPI repository using:

    pip install axem-dem

- The package name is 'axem-dem', but the command is `dem`.
- Ensure the Docker daemon is running before using DEM.

### Enable Autocompletion

Enable autocompletion for PowerShell, Bash, and Zsh shells:

    dem --install-completion

If the command doesn't work, specify your shell type as an input parameter (powershell, bash, or zsh).

> **Note for Zsh users:** `compinit` must be called from your .zshrc.

## Quick start

We got you covered in all scenarios!

### I'd like to start with a template...

DEM comes with a few templates available from the `axem` catalog. List them with:

    dem list --cat axem

Clone the selected template:

    dem clone DEV_ENV_NAME

Replace DEV_ENV_NAME with the name of the Development Environment you want to clone.

### I'd like to work on a project already configured with DEM...

Enter the project's root directory and initialize the DevEnv:

    dem init

### I'd like to use a DevEnv someone shared with me...

Import a DevEnv descriptor JSON:

    dem import PATH_TO_DEV_ENV

where PATH_TO_DEV_ENV is the path to the JSON file.

### I'd like to create my own DevEnv from scratch...

Create a new DevEnv:

    dem create DEV_ENV_NAME

Customize your DevEnv:
- Add or remove tools.
- Change the tool image for a given tool.

You can edit the DevEnv with:

    dem modify DEV_ENV_NAME

Finally, if you are ready to use the Development Environment, install it with:

    dem install DEV_ENV_NAME

>For more detailed instructions please refer to the
[Documentation](https://www.axemsolutions.io/dem_doc/index.html)

## The Concept in a Nutshell
A Development Environment (DevEnv) is a set of software tools used for a specific development 
project (e.g., build system, debugger, test framework).

The idea is to pack the tools separately into container images, which are then can be stored in 
registries.

Each DevEnv has a descriptor, like a blueprint, indicating which tools are required.

![DevEnv descriptor](/docs/wp-content/dev_env_descriptor.png)

Sample descriptors can be stored in the Development Environment **Catalogs**. You can browse these 
catalogs and download a copy of the Development Environment descriptor to your local catalog.

![Catalogs](/docs/wp-content/dem_catalogs.png)

A DevEnv can be installed from your local catalog.

![DevEnv installation](/docs/wp-content/dev_env_installation.png)
