## registries

The `registries` section of the configuration file is used to define the registries that DEM will 
use to search for images. 

**Default value:**

```json
"registries": [
    {
        "name": "axem",
        "namespace": "axemsolutions",
        "url": "https://registry.hub.docker.com"
    }
]
```

!!! info
    The Registry Management commands can be used to manage the registries in the configuration file.  

    - [`add-reg`](commands.md#dem-add-reg-name-url-namespace): Add a new registry to the configuration file.
    - [`del-reg`](commands.md#dem-del-reg-name): Delete a registry from the configuration file.
    - [`list-reg`](commands.md#dem-list-reg): List the registries in the configuration file.


## catalogs

The `catalogs` section of the configuration file is used to define the catalogs that DEM will use to
search for Development Environment descriptors.

** Default value: **

```json
"catalogs": [
    {
        "name": "axem",
        "url": "https://axemsolutions.io/dem/dev_env_org.json"
    }
]
```

!!! info
    The Catalog Management commands can be used to manage the catalogs in the configuration file.

    - [`add-cat`](commands.md#dem-add-cat-name-url): Add a new catalog to the configuration file.
    - [`del-cat`](commands.md#dem-del-cat-name): Delete a catalog from the configuration file.
    - [`list-cat`](commands.md#dem-list-cat): List the catalogs in the configuration file.

## hosts

!!! warning
    Remote hosts are not yet supported in DEM.

The `hosts` section of the configuration file is used to define the hosts that DEM will use as 
remote execution environments.

**Default value:**

```json
"hosts": []
```

!!! info
    The Host Management commands can be used to manage the hosts in the configuration file.

    - [`add-host`](commands.md#dem-add-host-name-url): Add a new host to the configuration file.
    - [`del-host`](commands.md#dem-del-host-name): Delete a host from the configuration file.
    - [`list-host`](commands.md#dem-list-host): List the hosts in the configuration file.

## http_request_timeout_s

The `http_request_timeout_s` section of the configuration file is used to define the timeout for
HTTP requests in seconds.

**Default value:**

```json
"http_request_timeout_s": 2
```

## use_native_system_cert_store

The `use_native_system_cert_store` section of the configuration file is used to define whether
the native system certificate store should be used for HTTPS requests or the default one provided
by the `certifi` package.

**Default value:**

```json
"use_native_system_cert_store": false
```

!!! info
    If the TLS authentication fails, try setting this value to `true`.