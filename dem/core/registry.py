""" Communicate with the registries. """
# dem/core/registry.py

from dem.core.core import Core
from dem.core.exceptions import RegistryError

import requests
from typing import Generator
from abc import ABC, abstractmethod

class Registry(Core, ABC):
    """ Abstract base class for a registry."""
    def __init__(self, registry_config: dict) -> None:
        """ Init the class.
        
            Args:
                registry_config -- container the name of the registry and its URL
        """
        try:
            self._url = registry_config["url"]
            self._name = registry_config["name"]
        except KeyError:
            raise RegistryError("Invalid registry configuration.")
        self._namespace = registry_config.get("namespace", "")
        self._repos = []

    @property
    @abstractmethod
    def _tag_endpoint_response_key(self) -> str:
        """ Used to obtain the tags from the endpoint response."""

    @property
    @abstractmethod
    def _repo_endpoint_response_key(self) -> str:
        """ Used to obtain the repositories from the endpoint response."""

    @abstractmethod
    def _append_repo_with_tag(self, endpoint_response: dict, repo: str) -> None:
        """ Get the tags from the endpoint response. Save the tags alongside with the actual repo
            in the private repo list.

            Args:
                endpoint_response -- the response from the endpoint
                repo -- append the tags of this repoistory
        """

    @abstractmethod
    def _get_repo_endpoint_url(self) -> str:
        """ The registry type specific endpoint to obtain the repositories.
        
            Returns with the endpoint url.
        """

    @abstractmethod
    def _get_tag_endpoint_url(self, repo_name: str) -> str:
        """ The registry type specific endpoint to obtain the tags.
        
            Args:
                repo_name -- we would like to get the tags for this repository
                
            Returns with the endpoint url.
        """

    def _list_tags(self, repo_name: str) -> None:
        """ Get the tags from the respective endpoint and call the registry specific function to 
            populate the private repo list.

            Args:
                repo_name -- get the tags of this repository
        """
        try:
            response = requests.get(self._get_tag_endpoint_url(repo_name), 
                                              timeout=self.config_file.http_request_timeout_s)
        except Exception as e:
            self.user_output.error(str(e))
        else:
            if response.status_code == requests.codes.ok:
                self._append_repo_with_tag(response.json(), repo_name)
                return
            else:
                self.user_output.error("Error in communication with the registry. Failed to retrieve tags. Response status code: " + str(response.status_code))

        self.user_output.msg("Skipping repository: " + repo_name)
    
    def _list_repos(self) -> Generator:
        """ Generator function for listing the repos. """
        try:
            response = requests.get(self._get_repo_endpoint_url(), 
                                    timeout=self.config_file.http_request_timeout_s)
        except Exception as e:
            self.user_output.error(str(e))
        else:
            if response.status_code == requests.codes.ok:
                try:
                    for repo in response.json()[self._repo_endpoint_response_key]:
                        yield "Loading image data from: " + repo["name"]
                        self._list_tags(repo["name"])
                    return
                except requests.exceptions.JSONDecodeError as e:
                    self.user_output.error(f"Invalid JSON format in response from the registry: {str(e)}")
                except Exception as e:
                    self.user_output.error(str(e))
            else:
                self.user_output.error("Error in communication with the registry. Failed to retrieve the repositories. Response status code: " + str(response.status_code))

        self.user_output.msg(f"Skipping [bold]{self._name}[/bold].")
    
    @property
    def repos(self) -> list[str]:
        """ Repos in the registry filtered by namespace if applicable.
        
            Returns with list of the repos.
        """
        self.user_output.status_generator(self._list_repos())
        return self._repos

class DockerHub(Registry):
    """ Docker Hub Registry
    
        Class variables:
            _docker_hub_domain -- the Docker Hub domain (used to determine if the config is for a 
                                  Docker Hub registry)
            _tag_endpoint_response_key -- used to obtain the tags from the endpoint response
            _repo_endpoint_response_key -- used to obtain the repositories from the endpoint response
    """
    _docker_hub_domain = "registry.hub.docker.com"
    _tag_endpoint_response_key = "results"
    _repo_endpoint_response_key = "results"

    def __init__(self, registry_config: dict) -> None:
        """ Init the class.
            
            Args:
                registry_config -- contains the name of the registry, its URL and optionally the
                                   namespace
        """
        super().__init__(registry_config)

        if not self._namespace:
            raise RegistryError("Invalid registry configuration. For Docker Hub the namespace must be set.")

    def _append_repo_with_tag(self, endpoint_response: dict, repo: str) -> None:
        """ Get the tags from the endpoint response. Save the tags alongside with the actual repo
            in the private repo list.

            Args:
                endpoint_response -- the response from the endpoint
                repo -- append the tags of this repoistory
        """
        for result in endpoint_response[self._tag_endpoint_response_key]:
            self._repos.append(self._namespace + "/" + repo + ":" + result["name"])

    def _get_repo_endpoint_url(self) -> str:
        """ Get the Docker Hub specific endpoint url to obtain the repositories.
            
            Returns with the endpoint url.
        """
        return f"{self._url}/v2/namespaces/{self._namespace}/repositories"

    def _get_tag_endpoint_url(self, repo_name: str) -> str:
        """ Get the Docker Hub specific endpoint url to obtain the tags.
            
            Args:
                repo_name -- we would like to get the tags for this repository

            Returns with the endpoint url.
        """
        return f"{self._url}/v2/namespaces/{self._namespace}/repositories/{repo_name}/tags"

class DockerRegistry(Registry):
    """ Docker Registry
    
        Class variables:
            _tag_endpoint_response_key -- used to obtain the tags from the endpoint response
            _repo_endpoint_response_key -- used to obtain the repositories from the endpoint response
    """
    _tag_endpoint_response_key = "tags"
    _repo_endpoint_response_key = "repositories"

    def _append_repo_with_tag(self, endpoint_response: dict, repo: str) -> None:
        """ Get the tags from the endpoint response. Save the tags alongside with the actual repo
            in the private repo list.

            Args:
                endpoint_response -- the response from the endpoint
                repo -- append the tags of this repoistory
        """
        for result in endpoint_response[self._tag_endpoint_response_key]:
            self._repos.append(self._url + "/" + repo + ":" + result)

    def _get_repo_endpoint_url(self) -> str:
        """ Get the Docker Registry specific endpoint url to obtain the repositories.
            
            Returns with the endpoint url.
        """
        return f"{self._url}/v2/_catalog"

    def _get_tag_endpoint_url(self, repo_name: str) -> str:
        """ Get the Docker Registry specific endpoint url to obtain the tags.
            
            Args:
                repo_name -- we would like to get the tags for this repository
                
            Returns with the endpoint url.
        """
        return f"{self._url}/v2/{repo_name.split('/')[1]}/tags/list"

class Registries(Core):
    """ Contains all configured registiries."""
    def __init__(self) -> None:
        """ Init the class by creating the registry instances."""
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
            self.registries.append(DockerHub(registry_config))
        else:
            self.registries.append(DockerRegistry(registry_config))

    def list_repos(self, reg_selection: list[str]) -> list[str]:
        """ List the available repositories.

            Args:
                reg_selection -- the selected registries, empty list means all registries
        
            Return with the list of repositories.
        """
        repo_list: list[str] = []

        for registry in self.registries:
            if not reg_selection or registry._name in reg_selection:
                repo_list.extend(registry.repos)

        return repo_list

    def add_registry(self, registry_config: dict) -> None:
        """ Add a new registry.
        
            Args:
                registry_config -- the registry to add
        """
        # Create the registry instance
        self._add_registry_instance(registry_config)

        # Add the registry config to the config file
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
                registry_config -- the registry to delete
        """
        for registry in self.registries.copy():
            if registry._name == registry_config["name"]:
                self.registries.remove(registry)

        self.config_file.registries.remove(registry_config)
        self.config_file.flush()