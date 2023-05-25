"""dev_env.json handling."""
# dem/core/data_management.py

from pathlib import PurePath
import os
import json, requests

_empty_dev_env_json = """
{
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

    def _create_empty_dev_env_json(self) -> None:
        """ If the dev_env.json doesn't exist, then create an emmpty one."""
        is_path_exist = os.path.exists(self._directory)
        if not is_path_exist:
            os.makedirs(self._directory)

        dev_env_json = open(self._path, "w")
        dev_env_json.write(_empty_dev_env_json)
        dev_env_json.close()

    def __init__(self) -> None:
        """ Init the class with an empty placeholder for the deserialized dev_env.json file. 
            Later this variable can be used to access the deserialized data. 
        """
        self.deserialized = None

    def read(self) -> dict:
        """ Read the deserialized dev_env.json."""
        try:
            dev_env_json = open(self._path, "r")
        except FileNotFoundError:
            self._create_empty_dev_env_json()
            self.deserialized = json.loads(_empty_dev_env_json)
        else:
            self.deserialized = json.load(dev_env_json)
            dev_env_json.close()
        
        return self.deserialized

    def write(self, deserialized: dict) -> None:
        """ Write modified deserialized data to the dev_env.json file.
            
            Args:
                deserialized -- the modified deserialized data
        """
        self.deserialized = deserialized
        dev_env_json = open(self._path, "w")
        json.dump(deserialized, dev_env_json, indent=4)
        dev_env_json.close()

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