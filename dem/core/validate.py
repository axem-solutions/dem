"""Validate the system."""
# dem/core/validate.py

from dem.core.data_management import get_deserialized_dev_env_json
from dem.core.exceptions import InvalidDevEnvJson
from dem.core.properties import __supported_dev_env_major_version__

def validate_dev_env_json():
    deserialized_dev_env_json = get_deserialized_dev_env_json()
    dev_env_json_major_version = int(deserialized_dev_env_json["version"].split('.', 1)[0])
    if dev_env_json_major_version != __supported_dev_env_major_version__:
        raise InvalidDevEnvJson("cia")
