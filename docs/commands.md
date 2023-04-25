## `dem list`

List the available Development Environments available locally or for the organization.

Arguments:

`DEV_ENV_NAME` Name of the Development Environment to get info about. [required]

Options:

- `--local` Scope is the local host.
- `--all` Scope is the organization.
- `--env` List the Development Environments.
- `--tool` List the tool images.

The following option combinations suppported:

      --local --env -> List the local Development Environments.
      --all --env -> List the organization's Development Environments.
      --local --tool -> List the local tool images.
      --all --tool -> List the tool images available in the axemsolutions registry.

## `dem info DEV_ENV_NAME`

Get information about the specified Development Environment.

## `dem pull DEV_ENV_NAME`

Arguments:

`DEV_ENV_NAME` Name of the Development Environment to install.  [required]

Pull all the required containerized tools from the registry and install the Development Environment 
locally.

    If a Development Environment with the same name, but different description has been already 
    available on the host PC, it gets overwritten with the new one.
    If the same Development Environment is already installed, but the installation is not complete, 
    the missing tool images get obtained from the registry.

## `dem create DEV_ENV_NAME`

Arguments:

`DEV_ENV_NAME` Name of the Development Environment to create.  [required]

Create a new Development Environment.

1. First you need to select the tool types.
2. Assign the required tool images for every selected types.

## `dem rename DEV_ENV_NAME NEW_DEV_ENV_NAME`

Arguments:

`DEV_ENV_NAME`      Name of the Development Environment to rename.  [required]
`NEW_DEV_ENV_NAME`  The new name.  [required]

Rename the Development Environment.

## `dem modify DEV_ENV_NAME`

Modify the tool types and required tool images for an existing Development Environment.

Arguments:

`DEV_ENV_NAME` Name of the Development Environment to modify.  [required]
