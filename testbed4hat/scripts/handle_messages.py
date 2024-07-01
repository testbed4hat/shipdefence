from datetime import datetime
import json
from pprint import pprint

import requests

# connection details
host = "https://serge-73772e6a84f6.herokuapp.com"
wargame = "wargame-l6nngxlk"
access = "umpire"


def get_logs_latest() -> list[dict]:
    response = requests.get(f"{host}/{wargame}/wargame-playerlogs/logs-latest")
    return response.json()["data"]


def get_wargame() -> list[dict]:
    response = requests.get(f"{host}/{wargame}")
    return response.json()["data"]

def get_wargame_definition() -> list[dict]:
    response = requests.get(f"{host}/{wargame}/last")
    return response.json()["data"]

def get_wargame_message() -> list[dict]:
    response = requests.get(f"{host}/{wargame}/lastDoc/id")
    return response.json()["data"]

#state of the world messages

#recommendation to target an incoming missile , launch missile against incoming
def post_wa_message() -> list[dict]:
    data = {
        'key1': 'value1',
        'key2': 'value2'
    }
    response = requests.post(f"{host}/{wargame}/", data)
    #need to know what key responses would be in

def post_core_mapping_message() -> list[dict]:
    data = {
        'key1': 'value1',
        'key2': 'value2'
    }
    response = requests.post(f"{host}/{wargame}/", data)
    #need to know what key responses would be in

if __name__ == "__main__":
    logs_data = get_logs_latest()
    pprint(logs_data)

    wargame_data = get_wargame()
    pprint(wargame_data[0])

    # Find the latest custom message
    message = next(
        (
            message
            for message in reversed(wargame_data)
            if message.get("messageType") == "CustomMessage"
            and "content" in message["message"]
        ),
    )
    pprint(message)

    # using the latest message as a template to send in a new message
    timestamp = datetime.utcnow().isoformat()
    message["message"].update({"content": f"New test message at {timestamp}"})
    message["details"].update({"timestamp": timestamp})
    message.update(
        {"_id": timestamp, "isOpen": False, "hasBeenRead": False, "_rev": None}
    )
    print(json.dumps(message))

    message_url = f"{host}/{wargame}"
    response = requests.put(
        message_url, json.dumps(message), headers={"Content-Type": "application/json"}
    )
    print(response.status_code)
    print(response.json())
