"""Docker registry management."""
# dem/core/registry.py

import dxf
import requests
import json

def auth(dxf_base_obj: dxf.DXFBase, response: requests.Response):
    with open("../password", "r") as password:
        password = password.read()
        dxf_base_obj.authenticate("axemsolutions", password=password[:-1], response=response)

def list_repos():
    r = requests.get("https://hub.docker.com/v2/repositories/axemsolutions")
    r_deserialized = json.loads(r.text)
    repos = r_deserialized["results"]
    images = []
    for repo in repos:
        for description in repo["description"].split(';'):
            description = description.split(':')
            print("\ttool name: " + description[0] + "\ttool version: " + description[1])
        print("")

        repo_path = "axemsolutions/" + repo["name"]
        dxf_obj = dxf.DXF("registry-1.docker.io", repo_path, auth=auth)

        for tag in dxf_obj.list_aliases():
            images.append(repo["name"] + ':' + tag)

    return images

if __name__ == "__main__":
    list_repos()