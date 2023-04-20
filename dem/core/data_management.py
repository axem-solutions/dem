"""dev_env.json handling."""
# dem/core/data_management.py

from pathlib import PurePath
import os
import json, requests

# Local dev_env.json

_empty_dev_env_json = """
{
    "version": "0.1",
    "org_name": "axem",
    "registry": "registry-1.docker.io",
    "development_environments": []
}
"""

class DevEnvJSON():
    _path = PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json")

    def _create_empty_dev_env_json(self) -> None:
        dev_env_json = open(self._path, "w")
        dev_env_json.write(_empty_dev_env_json)
        dev_env_json.close()

    def __init__(self) -> None:
        self.deserialized = ""

    def read(self) -> dict:
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
        self.deserialized = deserialized
        dev_env_json = open(self._path, "w")
        json.dump(deserialized, dev_env_json, indent=4)
        dev_env_json.close()

def read_deserialized_dev_env_json():
    dev_env_json = DevEnvJSON()
    return dev_env_json.read()

def write_deserialized_dev_env_json(dev_env_json_deserialized: dict) -> None:
    dev_env_json = DevEnvJSON()
    dev_env_json.write(dev_env_json_deserialized)

# Organization specific dev_env_org.json

def read_deserialized_dev_env_org_json():
    response = requests.get("https://axemsolutions.io/dem/dev_env_org.json")
    return response.json()