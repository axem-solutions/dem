"""Direct access to the registry over HTTP. or using the container engine."""
# dem/core/registry.py

from dem.core.core import Core
from dem.core.container_engine import ContainerEngine
from dem.core.data_management import ConfigFile
import requests
from typing import Generator
from abc import ABC, abstractmethod

class Registry(Core, ABC):
    """ Abstract base class for a registry."""
    def __init__(self, container_engine: ContainerEngine, registry_config: dict) -> None:
        """ Init the class.
        
            Args:
                container_engine -- the container engine
                registry_config -- container the name of the registry and its URL
        """
        self._container_engine = container_engine
        self._registry_config = registry_config
        self._repos = []

    @abstractmethod
    def _append_repo_with_tag(self, endpoint_response: dict, repo: str) -> None:
        """ Get the tags from the endpoint response. Save the tags alongside with the actual repo
            in the private repo list.
        """

    @abstractmethod
    def _get_tag_endpoint_url(self, repo_name: str) -> str:
        """ Get the registry specific endpoint to obtain the tags."""

    @abstractmethod
    def _list_repos_in_registry(self) -> Generator:
        """ Generator function for listing the repos. """

    def _list_tags(self, repo: str) -> None:
        """ Get the tags from the respective endpoint and call the registry specific function to 
            populate the private repo list.

            Args:
                repo -- get the tags of this repository
        """
        try:
            response = requests.get(self._get_tag_endpoint_url(repo), 
                                              timeout=self.config_file.http_request_timeout_s)
        except Exception as e:
            self.user_output.error(str(e))
        else:
            if response.status_code == requests.codes.ok:
                self._append_repo_with_tag(response.json(), repo)
                return
            else:
                self.user_output.error("Error in communication with the registry. Failed to retrieve tags. Response status code: " + str(response.status_code))

        self.user_output.msg("Skipping repository: " + repo)
    
    @property
    def repos(self) -> list[str]:
        """ Getter function for the repos in the registry.
        
            Returns with list of the repos.
        """
        self.user_output.status_generator(self._list_repos_in_registry())
        return self._repos

class DockerHub(Registry):
    """ Docker Hub Registry
    
        Class variables:
            _docker_hub_domain -- the Docker Hub domain (used to determine if the config is for a 
                                  Docker Hub registry)
            _tag_endpoint_response_key -- used to obtain the tags from the endpoint response
    """
    _docker_hub_domain = "registry.hub.docker.com"
    _tag_endpoint_response_key = "results"

    def _append_repo_with_tag(self, endpoint_response: dict, repo: str) -> None:
        """ Get the tags from the endpoint response. Save the tags alongside with the actual repo
            in the private repo list.

            Args:
                endpoint_response -- the response from the endpoint
                repo -- append the tags of this repoistory
        """
        for result in endpoint_response[self._tag_endpoint_response_key]:
            self._repos.append(repo + ":" + result["name"])

    def _get_tag_endpoint_url(self, repo: str) -> str:
        """ Get the Docker Hub specific endpoint url to obtain the tags.
            
            Args:
                repo -- we would like to get the tags for this repository
        """
        return self._registry_config["url"] + "/v2/repositories/" + repo + "/tags/"

    def _list_repos_in_registry(self) -> Generator:
        """ Generator function for listing the repos. """
        for repo in self._container_engine.search(self._registry_config["name"]):
            yield "Loading image data from: " + repo
            self._list_tags(repo)

class DockerRegistry(Registry):
    """ Docker Registry
    
        Class variables:
            _tag_endpoint_response_key -- used to obtain the tags from the endpoint response
    """
    _tag_endpoint_response_key = "tags"

    def _append_repo_with_tag(self, endpoint_response: dict, repo: str) -> None:
        """ Get the tags from the endpoint response. Save the tags alongside with the actual repo
            in the private repo list.

            Args:
                endpoint_response -- the response from the endpoint
                repo -- append the tags of this repoistory
        """
        for result in endpoint_response[self._tag_endpoint_response_key]:
            self._repos.append(repo + ":" + result)

    def _get_tag_endpoint_url(self, repo: str) -> str:
        """ Get the Docker Registry specific endpoint url to obtain the tags.
            
            Args:
                repo -- we would like to get the tags for this repository
        """
        return self._registry_config["url"] + "/v2/" + repo.split("/")[1] + "/tags/list"

    def _search(self) -> list[str]:
        """ Search the registry for the repositories
        
            Return with the repo list or an empty list if something bad happened.
        """
        repo_endpoint = self._registry_config["url"] + "/v2/_catalog"

        try:
            response = requests.get(repo_endpoint, timeout=self.config_file.http_request_timeout_s)
        except Exception as e:
            self.user_output.error(str(e))
        else:
            if response.status_code == requests.codes.ok:
                try:
                    return response.json()["repositories"]
                except requests.exceptions.JSONDecodeError as e:
                    self.user_output.error("Invalid JSON format in response. " + str(e))
                except Exception as e:
                    self.user_output.error(str(e))
            else:
                self.user_output.error("Error in communication with the registry. Failed to retrieve the repositories. Response status code: " + str(response.status_code))

        self.user_output.msg("Skipping registry: " + self._registry_config["name"])
        return []

    def _list_repos_in_registry(self) -> Generator:
        """ Generator function for listing the repos. """
        for repo_name in self._search():
            repo = self._registry_config["name"] + '/' + repo_name
            yield "Loading image data from: " + repo
            self._list_tags(repo)

class Registries(Core):
    """ Contains all configured registiries."""
    def __init__(self, container_engine: ContainerEngine) -> None:
        """ Init the class by creating the registry instances.
            
            Args:
                container_engine -- the container engine
                config_file -- config file that contains the registry parameters
        """
        self._container_engine = container_engine
        self.registries: list[Registry] = []
        for registry_config in self.config_file.registries:
            self._add_registry_instance(registry_config)
    
    def _add_registry_instance(self, registry_config: dict) -> None:
        """ Add a registry instance. Currently only the Docker Hub and Docker Registry registry 
            types are supported.
            
            Args:
                registry_config -- registry config
            """
        if DockerHub._docker_hub_domain in registry_config["url"]:
            self.registries.append(DockerHub(self._container_engine, registry_config))
        else:
            self.registries.append(DockerRegistry(self._container_engine, registry_config))

    def list_repos(self) -> list[str]:
        """ List the available repositories.
        
            Return with the list of repositories.
        """
        repo_list: list[str] = []

        for registry in self.registries:
            try:
                repo_list.extend(registry.repos)
            except Exception as e:
                self.user_output.error(str(e))
                self.user_output.error("[red]Error: The " + registry._registry_config["name"] + " registry is not available.[/]")

        return repo_list

    def add_registry(self, registry_config: dict) -> None:
        """ Add a new registry.
        
            Args:
                registry -- the registry to add
        """
        self._add_registry_instance(registry_config)

        self.config_file.registries.append(registry_config)
        self.config_file.flush()

    def list_registry_configs(self) -> list[dict]:
        """ List the registry configs. (As stored in the config file.)
        
            Returns with the list of the available registry configurations.
        """
        return self.config_file.registries

    def delete_registry(self, registry_config: dict) -> None:
        """ Delete the registry.
        
            Args:
                registry -- the registry to delete
        """
        for registry in self.registries.copy():
            if registry._registry_config == registry_config:
                self.registries.remove(registry)

        self.config_file.registries.remove(registry_config)
        self.config_file.flush()