---
title: Development Environments
---

## Development Environments

The dem assigns a set of tools for every project, these are called Development Environments. The
dem's functionality is based on the operation on the Development Environments.
Currently the following tool types are supported:

    - Build system
    - Toolchain
    - Debugger
    - Deployer
    - Test framework

When creating a new Development Environment the user can select any of the above tools and then 
assign the required tool images to them. 

!!! tip

    Check out the `dem create` command to learn more about creating a new Development Environment!

## Tool images

Tool images are the container images that have the specific tools built in. These images can be 
present

- on the host PC
- in a remote registry

!!! Note

    An image registry is a collection of image repositories.
    An image repository stores the different versions of the same image.

## Organization Development Environments

An organization can specify Development Environments which are available for every member. By 
default the dem only has access to the axem registry. The Development Environments defines here can 
be downloaded for free.

!!! warning

    Currently adding other organizations is not supported!

## Installing a Development Environment

Installation can be done with the `dem pull` command:
1. First installs the Development Environment descriptor.
2. Then downloads the tool images that are not yet available on the host PC.

!!! tip

    See the `dem pull` command for more details.
