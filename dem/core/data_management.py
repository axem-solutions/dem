"""json file handling."""
# dem/core/data_management.py

from typing import Any
from dem.core.properties import __config_dir_path__
from dem.core.exceptions import DataStorageError
from pathlib import PurePath
import os
import json

class BaseJSON():
    """ This class acts as an abstracted buffer over a json file. 
    
        If the buffer is not up-to-date it can be updated with update() which is a read from the 
        json file. If the buffer has newer data it can be written to file with flush().

        Class attributes: 
            _config_dir -- points to the json files' directory
            _path -- path to the json file (must be set in the descending classes)
            _default_json -- default json content
        """
    _config_dir = os.path.expanduser('~') + __config_dir_path__
    _path = ""
    _default_json = ""

    def _create_default_json(self) -> dict:
        """ If the .json doesn't exist, then create the default one.
        
            Return with the deserialized default json content. 
        """
        is_path_exist = os.path.exists(self._config_dir)
        if not is_path_exist:
            os.makedirs(self._config_dir)

        json_file = open(self._path, "w")
        json_file.write(self._default_json)
        json_file.close()

        return json.loads(self._default_json)

    def __init__(self) -> None:
        """ Init the class with an empty dict for the deserialized dev_env.json file. 
            Later this variable can be used to access the deserialized data. 
        """
        self.deserialized: dict[str, Any] = {}

    def update(self) -> None:
        """ Update the buffer with the content from the json file."""
        try: 
            json_file = open(self._path, "r")
        except FileNotFoundError:
            self.deserialized = self._create_default_json()
        else:
            self.deserialized = json.load(json_file)
            json_file.close()

    def flush(self) -> None:
        """ Write the buffer content to the json file."""
        json_file = open(self._path, "w")
        json.dump(self.deserialized, json_file, indent=4)
        json_file.close()

    def restore(self) -> None:
        """ Restore the json file to its default content."""
        self.deserialized = self._create_default_json()

class LocalDevEnvJSON(BaseJSON):
    """ Serialize and deserialize the dev_env.json file."""
    def __init__(self) -> None:
        """ Init the class."""
        self._path = PurePath(self._config_dir + "/dev_env.json")
        self._default_json = """{
    "version": "0.1",
    "org_name": "axem",
    "registry": "registry-1.docker.io",
    "development_environments": []
}
"""
        super().__init__()

    def update(self) -> None:
        try:
            super().update()
        except json.decoder.JSONDecodeError as e:
            raise DataStorageError(f"The dev_env.json file is corrupted.\n{str(e)}") from e

class ConfigFile(BaseJSON):
    """ Serialize and deserialize the config.json file."""
    def __init__(self) -> None:
        """ Init the class."""
        self._path = PurePath(self._config_dir + "/config.json")
        self._default_options = {
            "registries": [        
                {
                    "name": "axem",
                    "namespace": "axemsolutions",
                    "url": "https://registry.hub.docker.com"
                }
            ],
            "catalogs": [
                {
                    "name": "axem",
                    "url": "https://axemsolutions.io/dem/dev_env_org.json"
                }
            ],
            "hosts": [],
            "http_request_timeout_s": 2,
            "use_native_system_cert_store": False
        }
        self._default_json = json.dumps(self._default_options, indent=4)
        super().__init__()

    def update(self) -> None:
        try:
            super().update()
        except json.decoder.JSONDecodeError as e:
            raise DataStorageError(f"The config.json file is corrupted.\n{str(e)}") from e

        flush_needed = False

        self.registries: list[dict] | None = self.deserialized.get("registries", None)
        if self.registries is None:
            self.deserialized["registries"] = self._default_options["registries"]
            self.registries = self._default_options["registries"]
            flush_needed = True

        self.catalogs: list[dict] | None = self.deserialized.get("catalogs", None)
        if self.catalogs is None:
            self.deserialized["catalogs"] = self._default_options["catalogs"]
            self.catalogs = self._default_options["catalogs"]
            flush_needed = True

        self.hosts: list[dict] | None = self.deserialized.get("hosts", None)
        if self.hosts is None:
            self.deserialized["hosts"] = self._default_options["hosts"]
            self.hosts = self._default_options["hosts"]
            flush_needed = True

        self.http_request_timeout_s: float = self.deserialized.get("http_request_timeout_s", None)
        if self.http_request_timeout_s is None:
            self.deserialized["http_request_timeout_s"] = self._default_options["http_request_timeout_s"]
            self.http_request_timeout_s = self._default_options["http_request_timeout_s"]
            flush_needed = True

        self.use_native_system_cert_store: bool | None = self.deserialized.get("use_native_system_cert_store", None)
        if self.use_native_system_cert_store is None:
            self.deserialized["use_native_system_cert_store"] = self._default_options["use_native_system_cert_store"]
            self.use_native_system_cert_store = self._default_options["use_native_system_cert_store"]
            flush_needed = True

        if flush_needed:
            self.flush()