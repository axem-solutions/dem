---
title: Development Environment Settings
---

## run_tasks_as_current_user

Type: `bool`

Default: `false`

When set to `true`, DEM will run tasks as the current user, with the same UID and GID.
By default, tasks are run as the root user, but the UID and GID can be set using the `-u` as extra
arguments.

## enable_docker_network

Type: `bool`

Default: `false`

When set to `true`, DEM will enable the Docker network for the container. This allows the container 
to communicate with other containers on the same network.

!!! note
    This setting only enables the network. To make a container connected to this network, the 
    approriate settings must enabled in the task settings.