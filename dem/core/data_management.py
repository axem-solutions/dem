"""dev_env.json handling."""
# dem/core/data_management.py

from pathlib import PurePath
import os
import json

# Local dev_env.json

def read_deserialized_dev_env_json():
    dev_env_json_path = PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json")
    dev_env_json = open(dev_env_json_path, "r")
    deserialized_dev_env_json = json.load(dev_env_json)
    dev_env_json.close()
    return deserialized_dev_env_json

def write_deserialized_dev_env_json(dev_env_json_deserialized: dict) -> None:
    dev_env_json_path = PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json")
    dev_env_json = open(dev_env_json_path, "w")
    json.dump(dev_env_json_deserialized, dev_env_json, indent=4)
    dev_env_json.close()

# Organization specific dev_env_org.json

def read_deserialized_dev_env_org_json():
    #Get the raw json file.
    dev_env_org_json_path = PurePath("example_json/dev_env_org.json")
    dev_env_org_json = open(dev_env_org_json_path, "r")
<<<<<<< HEAD
    deserialized_dev_env_org_json = json.load(dev_env_org_json)
    dev_env_org_json.close()
    return deserialized_dev_env_org_json
=======

    return json.load(dev_env_org_json)

def write_dev_env_json(dev_env_json_deserialized: dict) -> None:
    pass
>>>>>>> 9ea2523 ('dem pull DEV_ENV_NAME' implemented. Only tested with already installed Dev Env.)
