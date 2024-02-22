---
title: The Basics
---

In this chapter we will cover the basic concepts of the Development Environment Manager (DEM).

## What is a Development Environment?
A set of software tools used for a specific development project is called a **Development
Environment**. These tools for example can be the build system, debugger, test framework, etc...

## A Container Image
To put it simply, a container image is a set of software components alongside its dependencies, 
which can be run in a container.

## A Tool Container Image
The idea is to build the tools from a Development Environment into their own respective images, so 
they can run isolatedly.

## Development Environment Descriptor
Each Development Environment has a descriptor. A descriptor, like a blueprint, indicates which tools
are required in the project, and the place their container images are stored.

![Dev Env descriptor](wp-content/dev_env_descriptor.png)

## Container Engine
The container engine is responsible for running the container images. The DEM uses the Docker
Container Engine to run the tool images.

## Registry and Repository
A registry serves as a storage for the tool images, where they can be kept without occupying space on 
the developer's computer. This storage enables convenient sharing of images with others, ensuring 
uniform tool usage among all collaborators on the same project.
When an image is uploaded to a registry, it initiates the creation of a repository. This repository 
is responsible for keeping track of the various versions of the image.

!!! Note

    An image **repository** stores the different versions of the same image.  
    An image **registry** is a collection of image repositories.

The DEM also uses registries in the background to store the tool images. To list the currently 
available registries use the `dem list-reg` command. The `dem add-reg` and `dem del-reg` commands 
can be used to add or delete registries.

!!! Note

    The DEM supports the [Docker Hub](https://docs.docker.com/docker-hub/) and 
    [Docker Registry](https://docs.docker.com/registry/)

    If you'd like to request support for other registry types, please create a 
    [new descussion](https://github.com/axem-solutions/dem/discussions/categories/regsitry).

## Development Environment Catalogs
A catalog is a collection of Development Environment descriptors.  
The DEM can handle multiple catalogs. To list the currently available ones use the `dem list-cat` 
command.  The `dem add-cat` and `dem del-cat` commands can be used to add or delete catalogs.

!!! Note

    axem has its own catalog, which is available by default.

The users can browse these catalogs, and download a copy of the Development Environment descriptor 
to their local catalog.

![Catalogs](wp-content/dem_catalogs.png)

## Development Platform
The registries, the catalogs, and the whole development infrastructure are part of the Development 
Platform. 