"""Hosts."""
# dem/core/hosts.py

from dem.core.data_management import ConfigFile
from dem.core.core import Core

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

class Hosts(Core):
    """ List of the available Hosts. """
    def __init__(self) -> None:
        """ Init the class with the host configurations.

            Args:
                config_file -- contains the host configurations
            """
        self.hosts: list[Host] = []
        for host_config in self.config_file.hosts:
            self._try_to_add_host(host_config)

    def _try_to_add_host(self, host_config: dict) -> bool:
        try:
            self.hosts.append(Host(host_config))
        except Exception as e:
            self.user_output.error(str(e))
            self.user_output.error("Error: Couldn't add this Host.")
            return False
        else:
            return True

    def add_host(self, host_config: dict) -> None:
        """ Add a new host.
        
            Args:
                catalog_config -- the new catalog to add
        """
        if self._try_to_add_host(host_config):
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
        for host in self.hosts.copy():
            if host.config == host_config:
                self.hosts.remove(host)

        self.config_file.hosts.remove(host_config)
        self.config_file.flush()