import docker

def get_local_image_tags() -> list[str]:
    docker_client = docker.from_env()
    local_image_tags = []

    for image in docker_client.images.list():
        for tag in image.tags:
            if tag:
                local_image_tags.append(tag)

    return local_image_tags