"""Development Environment Catalog."""
# dem/core/dev_env_catalog.py

from dem.core.dev_env import DevEnv
from dem.core.core import Core
from dem.core.exceptions import CatalogError
import requests

class DevEnvCatalog(Core):
    """ Development Environment Catalog. """
    def __init__(self, catalog_config: dict) -> None:
        """ Init the class. 

            The name of the catalog must be unique.

            Args:
                catalog_config -- the catalog description
        """
        self.config: dict = catalog_config
        self.url: str = catalog_config["url"]
        self.name: str = catalog_config["name"]
        self.dev_envs: list[DevEnv] = []

    def request_dev_envs(self) -> None:
        """ Request the Development Environments from the catalog. 
        
            Raises:
                CatalogError -- if the communication with the catalog fails
        """
        try:
            deser_json_response: requests.Response = requests.get(self.url, 
                                                                timeout=self.config_file.http_request_timeout_s)
        except Exception as e:
            raise CatalogError(f"Error in communication with the [bold]{self.name}[/bold] Development Environment Catalog.\n{str(e)}")

        if deser_json_response.status_code != requests.codes.ok:
            raise CatalogError(f"Error in communication with the [bold]{self.name}[/bold] Development Environment Catalog. " + 
                               "Failed to retrieve Development Environments." + 
                               "\nResponse status code: " + str(deser_json_response.status_code) + 
                               "\nDoes the URL point to a valid Development Environment Catalog?\n")

        try:
            for dev_env_descriptor in deser_json_response.json()["development_environments"]:
                self.dev_envs.append(DevEnv(descriptor=dev_env_descriptor))
        except Exception as e:
            raise CatalogError(f"The {self.name} Development Environment Catalog is corrupted.\n{str(e)}")

    def get_dev_env_by_name(self, dev_env_name: str) -> DevEnv | None:
        """ Get the Development Environment by name.
        
            Args:
                dev_env_name -- name of the Development Environment to get

            Return with the instance representing the Development Environment. If the Development 
            Environment doesn't exist in the catalog, return with None.
        """
        for dev_env in self.dev_envs:
            if dev_env.name == dev_env_name:
                return dev_env

class DevEnvCatalogs(Core):
    """ List of the available Development Environment Catalogs. """
    def __init__(self) -> None:
        """ Init the class with the catalogs from the config file."""
        self.catalogs: list[DevEnvCatalog] = []
        for catalog_config in self.config_file.catalogs:
            self.catalogs.append(DevEnvCatalog(catalog_config))

    def add_catalog(self, name: str, url:str) -> None:
        """ Add a new catalog.
        
            Args:
                name -- name of the catalog
                url -- url of the catalog

            Raises:
                CatalogError -- if the name is already used
        """
        for catalog in self.catalogs:
            if catalog.name == name:
                raise CatalogError(f"The {name} Development Environment Catalog name is already used.")

        catalog_config = {
            "name": name,
            "url": url
        }
        new_dev_env_catalog = DevEnvCatalog(catalog_config)
        # Request the Development Environments to validate the catalog.
        new_dev_env_catalog.request_dev_envs()

        self.catalogs.append(new_dev_env_catalog)
        self.config_file.catalogs.append(catalog_config)
        self.config_file.flush()

    def delete_catalog(self, name: str) -> None:
        """ Delete the catalog.
        
            Args:
                name -- name of the catalog to delete

            Raises:
                CatalogError -- if the catalog doesn't exist
        """
        for catalog in self.catalogs.copy():
            if catalog.name == name:
                self.catalogs.remove(catalog)
                break
        else:
            raise CatalogError(f"The {name} Development Environment Catalog doesn't exist.")

        self.config_file.catalogs.remove(catalog.config)
        self.config_file.flush()