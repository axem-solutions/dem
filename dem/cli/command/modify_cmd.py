"""modify CLI command implementation."""
# dem/cli/command/modify_cmd

def execute() -> None:
    derserialized_local_dev_nev = data_management.read_deserialized_dev_env_json()
    dev_env_local_setup = DevEnvLocalSetup(derserialized_local_dev_nev)