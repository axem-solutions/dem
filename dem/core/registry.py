"""Direct access to the registry over HTTP. 
Use the container engine when possible for accessing the registry. 
"""
# dem/core/registry.py

from dem.core.core import Core
from dem.core.container_engine import ContainerEngine
import requests
from dem.core import container_engine as container_engine
from dem.core.exceptions import RegistryError
from typing import Generator

class Registries(Core):
    """ Manages the registries."""
    def __init__(self, container_engine: ContainerEngine) -> None:
        """ Init the class.
        
            Args:
                container_engine -- communication is via the container engine if possible
        """
        self._container_engine = container_engine

    def _list_repos_generator(self, repo_list: list[str]) -> Generator:
        """ Generator function for listing the repos: returns the status at every image iteration
            for better feedback.
            
            Args:
                repo_list -- this list gets filled with the available repositories

            Return:
                The generator that provides the status.
            """
        registry = "axemsolutions"

        for image in self._container_engine.search(registry):
            yield "Loading image data from " + registry + ": " + image
            url = f"https://registry.hub.docker.com/v2/repositories/{image}/tags/"

            response = requests.get(url)

            if response.status_code == requests.codes.ok:
                for result in response.json()["results"]:
                    repo_list.append(image + ":" + result["name"])
            else:
                raise RegistryError("Error in communication with the registry. Failed to retrieve tags. Response status code: ",
                                    response.status_code)


    def list_repos(self) -> list[str]:
        """ List the available repositories.
        
            Return:
                The list of repositories.
        """
        repo_list: list[str] = []
        self.user_output.status_generator(self._list_repos_generator(repo_list))

        return repo_list