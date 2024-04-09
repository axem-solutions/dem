---
title: Quickstart
---

Now that you have the DEM installed, you might find yourself in one of the following scenarios:

## I'd like to start with a template...

Here at axem we'd like to create a template for every target out there. List the currently available
ones with:

    dem list --cat

You can clone the selected template with:

    dem clone DEV_ENV_NAME

## I'd like to work on a project already configured with DEM...

In this case you only need to initialize the Dev Env with:

    dem init

## I'd like to use a Dev Env someone shared with me...

You can import a Dev Env descriptor JSON with: 

    dem load DEV_ENV_NAME

## I'd like to create my own Dev Env from scratch...

Create a brand new Dev Env with the following command:

    dem create DEV_ENV_NAME

!!! info

    We believe that a project's dependencies should be stored in the project's repository. This way,
    every developer can use the same Development Environment. A Dev Env can be assigned to the 
    project with the `assign` command.

At this point you have the Development Environment's blueprint - its descriptor - in your local 
catalog, which you can modify to your needs. You might want to:

- Add/remove tools.
- Change the tool image for a given tool.

You can edit it with the Development Environment settings window:

    dem modify DEV_ENV_NAME

Finally, if you are ready to use it, you can install it with:

    dem install DEV_ENV_NAME

:tada: You are ready to start working with your Development Environment!

>For more detailed instructions about the commands please refer to the
[Commands chapter](commands.md).