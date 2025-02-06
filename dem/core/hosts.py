"""Hosts."""
# dem/core/hosts.py

from dem.core.core import Core
from dem.core.container_engine import ContainerEngine

class Host():
    """ A Host. """
    def __init__(self, host_config: dict) -> None:
        """ Init the class with the host config.

            Args:
                host_config -- the host config
        """
        self.config: dict = host_config
        self.name: str = host_config["name"]
        self.address: str = host_config["address"]
        self.container_engine: ContainerEngine = ContainerEngine(self.address)

class Hosts(Core):
    """ List of the available Hosts. """
    def __init__(self) -> None:
        """ Init the class with the host configurations.

            Args:
                config_file -- contains the host configurations
            """
        self.remotes: dict[str, Host] = {}

        local_host_config = {
            "name": "local",
            "address": "unix://var/run/docker.sock"
        }
        self.local = Host(local_host_config)

        for host_config in self.config_file.hosts:
            host = Host(host_config)
            self.remotes[host.name] = host

    def add_host(self, host_config: dict) -> None:
        """ Add a new host.
        
            Args:
                catalog_config -- the new catalog to add
        """
        host = Host(host_config)
        self.remotes[host.name] = host
        self.config_file.hosts.append(host_config)
        self.config_file.flush()

    def list_host_configs(self) -> list[dict]:
        """ List the host configs. (As stored in the config file.)
        
            Return with the list of the available host configurations.
        """
        return self.config_file.hosts

    def delete_host(self, host_config: dict) -> None:
        """ Delete the host.
        
            Args:
                host_config -- config of the host to delete
        """
        del self.remotes[host_config["name"]]
        self.config_file.hosts.remove(host_config)
        self.config_file.flush()

    def get_host_by_name(self, host_name: str) -> Host | None:
        """ Get the host by name.
        
            Args:
                host_name -- the host name

            Return with the host instance. If the host doesn't exist, return with None.
        """
        return self.remotes.get(host_name, None)