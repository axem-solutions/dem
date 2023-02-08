
# tests/core/test_dev_env_setup.py

import pytest
import dem.core.dev_env_setup as dev_env_setup
import tests.cli.test_data as test_data
import json

def test_invalid_dev_env_json_expect_error():
    with pytest.raises(LookupError) as exception_info:
        test_deserialized_dev_env_json = json.loads(test_data.invalid_dev_env_json)
        dev_env_setup_instance = dev_env_setup.DevEnvSetup(test_deserialized_dev_env_json)
        dev_env = dev_env_setup_instance.dev_envs[0]
        dev_env.validate()
    assert "Error in dev_env.json. The following tool type is not supported: build_system"