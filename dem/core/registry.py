"""Direct access to the registry over HTTP. 
Use the container engine when possible for accessing the registry. 
"""
# dem/core/registry.py

import json
import docker
import subprocess

def list_repos():
    registryimagelist = []
    images = []

    docker_client = docker.from_env()

    for repositories in docker_client.images.search("axemsolutions"):                
        registryimagelist.append(repositories['name'])
                
    for image in registryimagelist:        
        cmd = "docker trust inspect " + image        
        result = subprocess.run(cmd, shell=True,stdout=subprocess.PIPE)
        resultjson=json.loads(result.stdout.decode('UTF-8'))
        signedTags=resultjson[0]['SignedTags']
        for tag in signedTags:            
            images.append(image + ":" + tag['SignedTag'])
        
    return images

if __name__ == "__main__":
    list_repos()