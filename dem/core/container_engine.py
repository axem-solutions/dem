"""Docker image management."""
# dem/core/image_management.py

import docker

def get_local_image_tags() -> list[str]:
    docker_client = docker.from_env()
    local_image_tags = []

    for image in docker_client.images.list():
        for tag in image.tags:
            if tag:
                local_image_tags.append(tag)

    return local_image_tags


class ContainerEngine():
    def __init__(self) -> None:
        self.docker_client = docker.from_env()

    def get_local_image_tags(self) -> list[str]:
        local_image_tags = []

        for image in self.docker_client.images.list():
            for tag in image.tags:
                if tag:
                    local_image_tags.append(tag)

        return local_image_tags

    def pull(self, repository: str) -> None:
        self.docker_client.images.pull(repository=repository)