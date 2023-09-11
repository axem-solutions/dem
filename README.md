# Manage your containerized Development Environments with ease

<p align="center">
    <img alt="GitHub tag (with filter)" src="https://img.shields.io/github/v/tag/axem-solutions/dem?logo=github&color=79A7B5&link=https%3A%2F%2Fgithub.com%2Faxem-solutions%2Fdem%2Freleases">
    <img alt="GitHub issues" src="https://img.shields.io/github/issues/axem-solutions/dem?logo=github&color=2ea087&link=https%3A%2F%2Fgithub.com%2Faxem-solutions%2Fdem%2Fissues">
</p>

## Overview
The DEM is a command line tool that provides an easy, reproducible, and scalable way to set up 
Development Environments for embedded software development.

:star2: Contributors and early adopters are welcome! :star2:

> The DEM can be used locally, but it is in alpha state, so expect major new features!

<p align="center">
<strong>
<font size="4">
<a href="https://www.axemsolutions.io/dem_doc/index.html">Documentation</a> • <a href="https://www.axemsolutions.io/tutorial/index.html">Tutorial</a> 
</font>
</strong>
</p>

## Prerequisites

To be able to use the DEM on your PC, you need to have the following software installed:

- Python 3.10+
- Docker Engine 24.0+

:information_source: Currently only the Linux operating system is supported.

## Installation

DEM is available in the [PyPI repository](https://pypi.org/project/axem-dem/). Install it with:

    pip install axem-dem

:information_source: The package name is axem-dem, but the command is `dem`.

## Quick start

Installation of a preconfigured Development Environment can be done with a single command:

    dem pull DEV_ENV_NAME

Creating a new Development Environment is also very simple:

    dem create DEV_ENV_NAME

For more detailed instructions please refer to the 
[Documentation](https://www.axemsolutions.io/dem_doc/index.html)

## Key features

- Create scalable, reliable, and reproducible containerized Development Environments
- Manage your containerized tools
- Install preconfigured Development Environments from catalogs
- Ensure that everyone in the team works with the same toolset
- Share Development Environments outside of your organization
