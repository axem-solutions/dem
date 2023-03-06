"""dev_env.json handling."""
# dem/core/data_management.py

from pathlib import PurePath
import os
import json

def get_deserialized_dev_env_json():
    #Get the raw json file.
    dev_env_json_path = PurePath(os.path.expanduser('~') + "/.config/axem/dev_env.json")
    dev_env_json = open(dev_env_json_path, "r")

    return json.load(dev_env_json)

def get_deserialized_dev_env_org_json():
    #Get the raw json file.
    dev_env_org_json_path = PurePath("example_json/dev_env_org.json")
    dev_env_org_json = open(dev_env_org_json_path, "r")

    return json.load(dev_env_org_json)