"""dev_env.json handling."""
# dem/core/data_management.py

from pathlib import PurePath
from typing import Callable
import os, types
import json, requests

_empty_dev_env_json = """{
    "version": "0.1",
    "org_name": "axem",
    "registry": "registry-1.docker.io",
    "development_environments": []
}
"""

class LocalDevEnvJSON():
    """ Serialize and deserialize the dev_env.json file."""
    _path = PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json")
    _directory = PurePath(os.path.expanduser('~') + "/.config/axem")

    def _create_empty_dev_env_json(self) -> dict:
        """ If the dev_env.json doesn't exist, then create an empty one."""
        is_path_exist = os.path.exists(self._directory)
        if not is_path_exist:
            os.makedirs(self._directory)

        json_file = open(self._path, "w")
        json_file.write(_empty_dev_env_json)
        json_file.close()

        return json.loads(_empty_dev_env_json)

    @staticmethod
    def _invalid_json_callback(*args, **kwargs) -> None:
        pass

        return json.loads(_empty_dev_env_json)

    @staticmethod
    def _callback(*args, **kwargs) -> None:
        pass

    def __init__(self) -> None:
        """ Init the class with an empty dict for the deserialized dev_env.json file. 
            Later this variable can be used to access the deserialized data. 
        """
        self.deserialized = {}

    def read(self) -> dict:
        """ Read the deserialized dev_env.json."""
        try:
            json_file = open(self._path, "r")
        except FileNotFoundError:
            self.deserialized = self._create_empty_dev_env_json()
        else:
            try:
                self.deserialized = json.load(json_file)
            except json.decoder.JSONDecodeError:
                self._invalid_json_callback(msg="[red]Error: invalid json format.[/]", 
                                            user_confirm="Restore the original json file?")
                self.deserialized = self._create_empty_dev_env_json()
            else:
                json_file.close()
        
        return self.deserialized

    def write(self, deserialized: dict) -> None:
        """ Write modified deserialized data to the dev_env.json file.
            
            Args:
                deserialized -- the modified deserialized data
        """
        self.deserialized = deserialized
        json_file = open(self._path, "w")
        json.dump(deserialized, json_file, indent=4)
        json_file.close()

    def set_invalid_json_callback(self, invalid_json_callback: Callable):
        self._invalid_json_callback = types.MethodType(invalid_json_callback, self)

    def set_callback(self, callback_func: Callable):
        self._callback = types.MethodType(callback_func, self)

class OrgDevEnvJSON():
    """ Deserialize the dev_env_org.json file."""
    def __init__(self) -> None:
        """ Init the class with an empty placeholder for the deserialized dev_env_org.json file. 
            Later this variable can be used to access the deserialized data. 
        """
        self.deserialized = None

    def read(self) -> dict:
        """ Read the deserialized dev_env_org.json from the axemsolutions domain."""
        response = requests.get("https://axemsolutions.io/dem/dev_env_org.json")
        self.deserialized = response.json()
        return self.deserialized