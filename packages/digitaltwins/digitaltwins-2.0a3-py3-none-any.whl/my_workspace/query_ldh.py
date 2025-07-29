"""
Authentication: https://fairdomhub.org/api#section/Authentication
API token: gZRyhmDKsg9JSHdziu5ZrPR4DvjTdD4RgaDXTGDz
"""

import requests
import configparser

from pathlib import Path

if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini")
    configs = configparser.ConfigParser()
    configs.read(config_file)

    host = configs["seek"]["host"]
    port = configs["seek"]["port"]
    api_token = configs["seek"]["api_token"]

    base_url = host + ":" + port

    print("programmes:")
    url = base_url + "/programmes"

    headers = {
        "Authorization": "Bearer " + api_token,
        "Accept": "application/json"
    }

    resp = requests.get(url, headers=headers)
    # resp.raise_for_status()
    data = resp.json().get("data")
    print(data)

    print("programme 2:")
    id = 2
    url = base_url + "/programmes/" + str(id)
    resp = requests.get(url, headers=headers)
    data = resp.json().get("data")
    print(data)

    print("projects:")
    url = base_url + "/projects"
    resp = requests.get(url, headers=headers)
    data = resp.json()
    print(data)

    print("project 3:")
    project_id = 3
    url = base_url + "/projects/" + str(project_id)
    resp = requests.get(url, headers=headers)
    data = resp.json()
    print(data)

