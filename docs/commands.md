---
title: Commands
---

#Commands

!!! question "Bug report"

    We encourage you to join our open-source community. 
    If you find any errors, inaccuracies, or have suggestions to improve our documentation or tool, please report your findings on [GitHub](https://github.com/axem-solutions/dem/issues) or start a conversation in our community through [Discord](https://discord.gg/3aHuJBNvrJ).

# Development Environment management


## **`dem add-task DEV_ENV_NAME TASK_NAME COMMAND`**

**Description:**

Add a new task to the Development Environment.

A task is a command that can be run in the context of the Development Environment. 
The task can be run with the `dem run` command. 

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment.                    | :material-check:|
| `TASK_NAME`      | Name of the task.                                       | :material-check:|
| `COMMAND`        | Command to run. Must be enclosed with quotes.           | :material-check:|

**Examples:**

| Example            | Description                                             |
|--------------------|---------------------------------------------------------|
| `dem add-task dev_env_name list-dir "ls -la"`     | Add a new command called `list-dir` that lists the content of the current directory. The task can be executed with `dem run dev_env_name list-dir`. |
| `dem add-task dev_env_name build "docker run --rm -v \"$(pwd)\":/work axemsolutions/make_gnu-arm:13.2 make"`     | Add a new command called `build` that builds the project in a docker container. The task can be executed with `dem run dev_env_name build`. |

---

## **`dem assign DEV_ENV_NAME, [PROJECT_PATH]`**

**Description:**

Assign a Development Environment to a project.

 If the project already has a Development Environment assigned, the user will be asked if they want to
overwrite it or not.
 Projects that have a Development Environment assigned, can be initialized with the `init` command.

**Arguments:**

| Argument                  | Description                                    | Required                             |
| --------------------------| ---------------------------------------------- | :------------------------------------: |
| `DEV_ENV_NAME`            | Name of the Development Environment to assign.  | :material-check:                   |
| `[PROJECT_PATH]`          | Path of the project to assign the Development Environment to. If not set, the current working directory will be used. | |


---

## **`dem clone DEV_ENV_NAME`**

**Description:**

Clone a Development Environment descriptor from the catalogs. 

Only the Development Environment descriptor will be cloned, the required tool images won't be pulled. If a Development Environment with the same name has been already available on the host PC, the user will be asked if they want to overwrite it or not.

:information_source: After cloning, the Development Environment can be installed with the `install` command.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`   | Clone the descriptor of the Dev Env.                    | :material-check:|

---

## **`dem cp DEV_ENV_NAME NEW_DEV_ENV_NAME`**

**Description:**

Create a copy of an existing local Development Environment.

**Arguments:**

| Argument           | Description                                       | Required        |
|--------------------|---------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`     | Name of the Development Environment to copy.      | :material-check:|
| `NEW_DEV_ENV_NAME` | Name of the New Development Environment.          | :material-check:|

---

## **`dem create DEV_ENV_NAME`**

**Description:**

Create a new Development Environment descriptor and save it to the local descriptor storage (catalog).

Running this command will open up the Dev Env Settings Window:

![Dev Env Settings Window](wp-content/dev_env_settings_window.png)

There are two options to add new tools to the Development Environment:

1. **Add Tool Images by name**: You can add tool images by typing their name in the input field. 
The format should be the same as one would use with the `docker pull` command 
({registry}/{image}:{tag}).
2. **Add Tool Images by selecting**: You can select the tool images from the tool image selector 
table. This table contains all the available tool images from the registries that are added to DEM. 
You can navigate with the :material-arrow-up: and :material-arrow-down: or :material-alpha-k:
and :material-alpha-j: keys. The table can be filtered by typing in the search bar.

On the right side, you can see the tool images that are selected.

When the Dev Env is ready, click or press :material-keyboard-return: on the `Save` button.

!!! info 

    After creation, the Development Environment can be installed with the `install` command.


**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment to create.          | :material-check:|

---

## **`dem delete DEV_ENV_NAME`**

**Description:**

Delete the Dev Env descriptor from the local descriptor storage. If the Dev Env is installed, the user will be asked whether they want to uninstall it.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment to delete.          | :material-check:|

---

## **`dem del-task DEV_ENV_NAME TASK_NAME`**

**Description:**

Delete a task from the Development Environment.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment.                    | :material-check:|
| `TASK_NAME`      | Name of the task to delete.                             | :material-check:|

---

## **`dem export DEV_ENV_NAME [PATH_TO_EXPORT]`**

**Description:**

Export a Development Environment descriptor in JSON format to a text file. 

This file can be imported with the `import` command on another host.

The way the file gets named can be set by the `PATH_TO_EXPORT` argument:

- **Not set**: The file gets saved to the current directory with the name of the Development 
Environment and without extension.
- **Only a name is set**: The file gets saved with that name to the current directory, optionally 
with the set extension.
- **The argument is a directory path**: The file gets saved there with the name of the Development 
Environment, without extension.
- **The argument is a path with the file name**: The exported content gets saved into that file.
The extension can be set with the file name.

!!! Note

    The exported file only contains the Development Environment descriptor in JSON format. For a 
    successful import the DEM needs access to all the registries where the required images are 
    stored.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`   | The name of the Development Environment to export.      | :material-check:|
| `[PATH_TO_EXPORT]` | Where to save the exported descriptor in JSON format. If not set, the current directory will be used. |  |

---

## **`dem import PATH_TO_DEV_ENV`**

**Description:**

Imports a Development Environment descriptor.

:information_source: After the import, the Development Environment can be installed with the `install` 
command.

!!! Note

    The file to import only contains the Development Environment descriptor. To install the Dev Env
    the DEM needs access to all the registries where the required images are stored.


**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `PATH_TO_DEV_ENV`| Path of the JSON file to import.                        | :material-check:|

---

## **`dem info DEV_ENV_NAME [OPTIONS] [*CATALOG_NAMES]`**

**Description:**

Get information about the specified Development Environment available locally or in the catalogs.

**Options:**

| Options             | Description                                             |
|--------------------|---------------------------------------------------------|
| `--cat`            | DEM will search for the Dev Env in the catalogs and will print the details of the first match. You can specifiy the catalogs' name to search in after this option. If no catalog is specified, all the available catalogs will be used. If the Dev Env is not found in the catalogs, an error message will be printed.  |



:information_source: Autocomplete only works with the locally avialable Dev Envs.

**Arguments:**

| Argument           | Description                                             | Required        |
|--------------------|---------------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`     | Name of the Development Environment to get info about.  | :material-check:|
| `[OPTIONS]`        | `--cat`: Search in the catalogs.                        |                 |
| `[*CATALOG_NAMES]` | List of catalogs to search in (separated by space).                                  |                 |

**Examples:**

| Example            | Description                                             |
|--------------------|---------------------------------------------------------|
| `dem info dev_env_name`     | Get information about the **locally** available Development Environment.  |
| `dem info dev_env_name --cat`     | Get information about the Development Environment from the **catalogs**.  |
| `dem info dev_env_name --cat catalog1 catalog2`     | Get information about the Development Environment from the **catalog1 and catalog2**.  |


---

## **`dem init [PROJECT_PATH]`**

**Description:**

Initialize a project with the assigned Development Environment.

:information_source: After the initialization, the Development Environment can be installed with the `install` 
command.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `[PROJECT_PATH]` | Path of the project to initialize. If not set, the current working directory will be used. |                  |

---

## **`dem install DEV_ENV_NAME`**

**Description:**

Install the selected Development Environment. DEM pulls all the required containerized tools to the 
appropriate hosts defined by the assigned tasks. 

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment to install.         | :material-check:|

---

## **`dem list [OPTIONS] [*CATALOG_NAMES]`**

**Description:**

List the locally available Dev Envs.

**Options:**

| Options            | Description                                             |
|--------------------|---------------------------------------------------------|
| `--cat`            | List the available Dev Envs from the catalogs. Specify the catalogs' name to list the Dev Envs from. More then one catalog can be specified. If no catalog is specified, all the available catalogs will be used.  |



**Arguments:**

| Argument           | Description                                                       | Required        |
|--------------------|-------------------------------------------------------------------|:---------------:|
| `[OPTIONS]`        | `--cat`: List the Dev Envs from the catalogs.                     |                 |
| `[*CATALOG_NAMES]` | List of catalogs to list the Dev Envs from (separated by space).  |                 |

**Examples:**

| Example            | Description                                             |
|--------------------|---------------------------------------------------------|
| `dem list`     | List the **locally** available Dev Envs.  |
| `dem list --cat`     | List all the Dev Envs from **all** the available **catalogs**.  |
| `dem list --cat catalog1 catalog2`     | List all the Dev Envs from the **catalog1 and catalog2.**  |

---

## **`dem list-tools [OPTIONS] [*REGISTRY_NAMES]`**

**Description:**

List the available tools.

**Options:**

| Options             | Description                                             |
|--------------------|---------------------------------------------------------|
| `--reg`            | List the available tools from the registries. Specify the registries' name to list the tools from. More then one registry can be specified. If no registry is specified, all the available registries will be used.  |


**Arguments:**

| Argument           | Description                                                      | Required        |
|--------------------|------------------------------------------------------------------|:---------------:|
| `[OPTIONS]`        | `--reg`: List the tools from the registries.                     |                 |
| `[*REGISTRY_NAMES]`| Registries to list the tools from (separated by space).          |                 |

**Examples:**

| Example            | Description                                             |
|--------------------|---------------------------------------------------------|
| `dem list-tools`     | List the **locally** available tools.  |
| `dem list-tools --reg`     | List all the tools from **all** the available **registries**.  |
| `dem list-tools --reg registry1 registry2`     | List all the tools from the **registry1** and **registry2.**  |

---

## **`dem modify DEV_ENV_NAME`**

**Description:**

Modify a Development Environment descriptor available from the local descriptor storage (catalog).

Running this command will open up the Dev Env Settings Window, prefilled with the DevEnv's actual
state:

![Dev Env Settings Window](wp-content/dev_env_settings_window.png)

There are two options to add new tools to the Development Environment:

1. **Add Tool Images by name**: You can add tool images by typing their name in the input field. 
The format should be the same as one would use with the `docker pull` command 
({registry}/{image}:{tag}).
2. **Add Tool Images by selecting**: You can select the tool images from the tool image selector 
table. This table contains all the available tool images from the registries that are added to DEM. 
You can navigate with the :material-arrow-up: and :material-arrow-down: or :material-alpha-k:
and :material-alpha-j: keys. The table can be filtered by typing in the search bar.

On the right side, you can see the tool images that are selected.

When the Dev Env is ready, click or press :material-keyboard-return: on the `Save` button.

!!! info 

    After the modification, the Development Environment can be installed with the `install` command.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|:---------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment to modify.          | :material-check:|

---

## **`dem rename DEV_ENV_NAME NEW_DEV_ENV_NAME`**

**Description:**

Rename the Development Environment.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment to rename.          | :material-check:|
| `NEW_DEV_ENV_NAME`| The new name.                                          | :material-check:|

---

## **`dem run [DEV_ENV_NAME] TASK_NAME [OPTIONS]`**

**Description:**

Run the task of the Development Environment. The Dev Env must be installed.

If the Dev Env is not specified, the default Dev Env will be used. If the default Dev Env is not
set, an error message will be printed.

**Options:**

| Options             | Description                                             |
|---------------------|---------------------------------------------------------|
| `--extra-args`      | Additional arguments to pass to the container           |

**Arguments:**

| Argument         | Description                                              | Required        |
|------------------|----------------------------------------------------------|----------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment to run the task in. If not set, the default Dev Env will be used. | 
| `TASK_NAME`      | The name of the task to run.                             | :material-check:|

---

## **`dem set-default DEV_ENV_NAME`**

**Description:**

Set the selected Development Environment as the default one.

The default Development Environment is used when the `dem run` command is run without specifying a
Development Environment.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment to set as default.  | :material-check:|

---

## **`dem uninstall DEV_ENV_NAME`**

**Description:**

Uninstall the selected Development Environment.

Sets the installed flag to False. DEM checks whether 
a tool image is required or not by any of the remaining installed local Development Environments. In case the tool image is not required anymore, the DEM tries to delete it. 

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `DEV_ENV_NAME`   | Name of the Development Environment to uninstall.       | :material-check:|

---

# Catalog management


## **`dem add-cat NAME URL`**

**Description:**

Add a new catalog.

You can name the catalog as you wish.
The URL must point to an HTTP(S) server where the Catalog JSON file is available.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `NAME`           | Name of the catalog to add.                             | :material-check:|
| `URL`            | URL of the catalog file.                                | :material-check:|

---

## **`dem del-cat NAME`**

**Description:**

Delete a catalog.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `NAME`           | Name of the catalog to delete.                          | :material-check:|

---

## **`dem list-cat`**

**Description:**

List the available catalogs.

---

# Registry management


## **`dem add-reg NAME URL [NAMESPACE]`**

**Description:**

Add a new registry.

The name of the registry must be unique. The URL must point to the registry's API. 

The namespace is only required for the Docker Hub.

Examples:

*Add a Docker Hub registry called `axem` with the namespace `axemsolutions`*

```bash
dem add-reg axem https://registry.hub.docker.com axemsolutions
```

*Add a self-hosted registry called `local`*

```bash
dem add-reg local http://localhost:5000
```

!!! Note

    The Docker Hub API URL is https://registry.hub.docker.com.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `NAME`           | Unique name for the registry.                           | :material-check:|
| `URL`            | API URL of the registry.                                | :material-check:|
| `NAMESPACE`      | Namespace inside the registry.                          |                 |

---

## **`dem del-reg NAME`**

**Description:**

Delete a registry.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `NAME`           | Name of the registry to delete.                         | :material-check:|

---

## **`dem list-reg`**

**Description:**

List the available registries.

---

# Host management


## **`dem add-host NAME ADDRESS`**

**Description:**

Add a new host to the configuration.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `NAME`           | Name of the host.                                       | :material-check:|
| `ADDRESS`        | IP or hostname of the host.                             | :material-check:|

---

## **`dem del-host NAME`**

**Description:**

Delete a host from the config file.

**Arguments:**

| Argument         | Description                                             | Required        |
|------------------|---------------------------------------------------------|----------------:|
| `NAME`           | Name of the host to delete.                             | :material-check:|

---

## **`dem list-host`**

**Description:**

List the available hosts from the config file.

