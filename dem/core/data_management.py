"""json file handling."""
# dem/core/data_management.py

from dem.core.core import Core
from dem.core.properties import __config_dir_path__
from pathlib import PurePath
import os
import json, requests

class BaseJSON(Core):
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
        self.deserialized = {}
        self.update()

    def update(self) -> None:
        """ Update the buffer with the content from the json file."""
        try: 
            json_file = open(self._path, "r")
        except FileNotFoundError:
            self.deserialized = self._create_default_json()
        else:
            try:
                self.deserialized = json.load(json_file)
            except json.decoder.JSONDecodeError:
                self.user_output.get_confirm("[red]Error: invalid json format.[/]", 
                                             "Restore the original json file?")
                self.deserialized = self._create_default_json()
            else:
                json_file.close()

    def flush(self) -> None:
        """ Write the buffer content to the json file."""
        json_file = open(self._path, "w")
        json.dump(self.deserialized, json_file, indent=4)
        json_file.close()

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

class ConfigFile(BaseJSON):
    """ Serialize and deserialize the config.json file."""
    def __init__(self) -> None:
        """ Init the class."""
        self._path = PurePath(self._config_dir + "/config.json")
        self._default_json = """{
    "registries": [
        {
            "name": "axemsolutions",
            "url": "https://registry.hub.docker.com"
        }
    ],
    "catalogs": [
        {
            "name": "axem",
            "url": "https://axemsolutions.io/dem/dev_env_org.json"
        }
    ]
}"""
        super().__init__()

        self.registries: list[dict] = self.deserialized["registries"]
        self.catalogs: list[dict] = self.deserialized["catalogs"]