"""Docker registry management."""
# dem/core/registry.py

import requests
import json

def list_repos():
    r = requests.get("https://hub.docker.com/v2/repositories/axemsolutions")
    r_deserialized = json.loads(r.text)
    repos = r_deserialized["results"]
    for repo in repos:
        print("Image name: " + repo["name"])
        for description in repo["description"].split(';'):
            description = description.split(':')
            print("\ttool name: " + description[0] + "\ttool version: " + description[1])
        print("")

if __name__ == "__main__":
    list_repos()