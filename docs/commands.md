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

---

## `dem info DEV_ENV_NAME`

Arguments:

`DEV_ENV_NAME` Name of the Development Environment to get info about.[required]

Get information about the specified Development Environment.

---

## `dem pull DEV_ENV_NAME`

Arguments:

`DEV_ENV_NAME` Name of the Development Environment to install.  [required]

Pull all the required containerized tools from the registry and install the Development Environment 
locally.

    If a Development Environment with the same name, but different description has been already 
    available on the host PC, it gets overwritten with the new one.
    If the same Development Environment is already installed, but the installation is not complete, 
    the missing tool images get obtained from the registry.

---

## `dem create DEV_ENV_NAME`

Arguments:

`DEV_ENV_NAME` Name of the Development Environment to create.  [required]

Create a new Development Environment.

1. First you need to select the tool types.
2. Assign the required tool images for the selected types.

---

## `dem rename DEV_ENV_NAME NEW_DEV_ENV_NAME`

Arguments:

`DEV_ENV_NAME`      Name of the Development Environment to rename.  [required]
`NEW_DEV_ENV_NAME`  The new name.  [required]

Rename the Development Environment.

---

## `dem modify DEV_ENV_NAME`

Arguments:

`DEV_ENV_NAME` Name of the Development Environment to modify.  [required]

Modify the tool types and required tool images for an existing Development Environment.

1. The DEM shows a list of the already selected tools. You can modify the selection.
2. Assign the required tool images for the selected types. If a tool type was already selected in 
the original Development Environment, the same tool image gets preselected - you only need to press 
the enter if you don't want to change it.

---

## `dem delete DEV_ENV_NAME`

Arguments:

  DEV_ENV_NAME  Name of the Development Environment to delete.  [required]

Delete the Development Environment from the dev_env.json. If a tool image is not required  anymore 
by any of the avaialable local Developtment Environments, the DEM asks the user if they want to 
delete that image or keep it.

!!! warning

    You can't undo this command!