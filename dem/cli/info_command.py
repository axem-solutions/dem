import dem.core.data_management as data_management
import docker 

def execute() -> None:
    data_management.get_deserialized_dev_env_json()

    docker_client = docker.from_env()
    docker_client.images.list()