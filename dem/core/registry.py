"""Direct access to the registry over HTTP. 
Use the container engine when possible for accessing the registry. 
"""
# dem/core/registry.py

import requests
from dem.core import container_engine as container_engine
from dem.core.exceptions import RegistryError

def list_repos(container_engine_obj: container_engine.ContainerEngine) -> list[str]:
    registry = "axemsolutions"
    images = []
    
    for image in container_engine_obj.search(registry):
        url = f"https://registry.hub.docker.com/v2/repositories/{image}/tags/"

        response = requests.get(url)

        if response.status_code == requests.codes.ok:
            for result in response.json()["results"]:
                images.append(image + ":" + result["name"])
        else:
            raise RegistryError("Error in communication with the registry. Failed to retrieve tags. Response status code: ",
                                response.status_code)

    # images = [
    #     "axemsolutions/make_gnu_arm:latest",
    #     "axemsolutions/make_gnu_arm:latest3",
    #     "asdfjaésdjf:le",
    #     "ipueiwrqwer:cica",
    #     "cnxyvcxymé:v0.1",
    # ]

    return images