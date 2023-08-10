"""Direct access to the registry over HTTP. or using the container engine."""
# dem/core/registry.py

from dem.core.core import Core
from dem.core.container_engine import ContainerEngine
from dem.core.exceptions import RegistryError
from dem.core.data_management import ConfigFile
from dem.core import container_engine as container_engine
import requests
from typing import Generator

class Registries(Core):
    """ Manages the registries."""
    def __init__(self, container_engine: ContainerEngine, config_file: ConfigFile) -> None:
        """ Init the class.
        
            Args:
                _container_engine -- communication is via the container engine if possible
                _config_file -- contains the list of available registries
        """
        self._container_engine = container_engine
        self._config_file = config_file

    def _list_repos_in_registry(self, registry: dict, repo_list: list[str]) -> Generator:
        """ Generator function for listing the repos. 
        
            Returns the status at every image iteration for better feedback.
            
            Args:
                registry -- the registry to get the repos from
                repo_list -- this list gets filled with the available repositories

            Return with the generator that provides the status.
            """
        for image in self._container_engine.search(registry["name"]):
            yield "Loading image data from " + registry["name"] + ": " + image
            url = registry["url"] + "repositories/" + image + "/tags/"

            try:
                response = requests.get(url)
            except requests.exceptions.MissingSchema as e:
                self.user_output.error(str(e))
                self.user_output.msg("Skipping this repository.")
            else:
                if response.status_code == requests.codes.ok:
                    for result in response.json()["results"]:
                        repo_list.append(image + ":" + result["name"])
                else:
                    raise RegistryError("Error in communication with the registry. Failed to retrieve tags. Response status code: ",
                                        response.status_code)

    def list_repos(self) -> list[str]:
        """ List the available repositories.
        
            Return with the list of repositories.
        """
        repo_list: list[str] = []
        for registry in self._config_file.registries:
            self.user_output.status_generator(self._list_repos_in_registry(registry, repo_list))

        return repo_list

    def add_registry(self, registry: dict) -> None:
        """ Add a new registry to the config.
        
            Args:
                registry -- the registry to add
        """
        self._config_file.registries.append(registry)
        self._config_file.flush()

    def list_registries(self) -> list[dict]:
        """ List the available registries in the config.
        
            Returns with the list of the available registries.
        """
        return self._config_file.registries