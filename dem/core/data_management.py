"""dev_env.json handling."""
# dem/core/data_management.py

from pathlib import Path
import os
import json

def get_deserialized_dev_env_json():
	#Get the raw json file.
	dev_env_json_path = Path(os.path.expanduser('~') + "/.config/axem/dev_env.json")
	dev_env_json = open(dev_env_json_path, "r")

	#Parse the json file.
	dev_env_json_deserialized = json.load(dev_env_json)

	return dev_env_json_deserialized