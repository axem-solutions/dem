"""Development Environment Catalog."""
# dem/core/dev_env_catalog.py

from dem.core.dev_env import DevEnv
from dem.core.data_management import ConfigFile
import requests

class DevEnvCatalog():
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.dev_envs: list[DevEnv] = []
        for dev_env_descriptor in requests.get(url).json()["development_environments"]:
            self.dev_envs.append(DevEnv(descriptor=dev_env_descriptor))

    def get_dev_env_by_name(self, dev_env_name: str) -> DevEnv | None:
        """Get the Development Environment by name.
        
            Args:
                dev_env_name -- name of the Development Environment to get
            Returns with the instance representing the Development Environment. If the Development 
            Environment doesn't exist in the catalog, the function returns with None.
        """
        for dev_env in self.dev_envs:
            if dev_env.name == dev_env_name:
                return dev_env

class DevEnvCatalogs():
    def __init__(self, config_file: ConfigFile) -> None:
        self._config_file: ConfigFile = config_file
        self.catalogs: list[DevEnvCatalog] = []
        for catalog_config in config_file.catalogs:
            self.catalogs.append(DevEnvCatalog(catalog_config["url"]))

    def add_catalog(self, catalog_config: dict) -> None:
        """ Add a new catalog.
        
            Args:
                catalog_config -- the new catalog to add
        """
        self.catalogs.append(DevEnvCatalog(catalog_config["url"]))

        self._config_file.catalogs.append(catalog_config)
        self._config_file.flush()