from datetime import date, datetime, time, timedelta, UTC
import json
import requests


class SergeGame:
    ID_CO_A = "co-alpha"
    ID_CO_B = "co-bravo"
    ID_AI = "ai-assistant"
    TARGETING_CHANNEL_A = "channel-wa-alpha"
    TARGETING_CHANNEL_B = "channel-wa-bravo"

    MAPPING_CHANNEL = {
        1: TARGETING_CHANNEL_A,
        2: TARGETING_CHANNEL_B,
    }
    MAPPING_SHIP = {
        0: "None",
        1: "Ship A",
        2: "Ship B",
    }
    MAPPING_WEAPON = {0: "None", 1: "Short Range", 2: "Long Range"}

    def __init__(self, game_id: str, server_url: str = "https://serge-inet.herokuapp.com"):
        self.url = server_url
        self.game_id = game_id
        self.last_msg_id = None
        self.api_endpoint = f"{self.url}/{self.game_id}"

        # initialize the game state
        self.turn_number: int = 0
        self.phase: str = "adjudication"
        self.game_time: time = time(hour=15, minute=0)  # TODO: to read from the game definition

    def get_new_messages(self) -> list[dict]:
        new_messages = self.get_messages(since_msg_id=self.last_msg_id)
        if new_messages:
            self.last_msg_id = new_messages[-1]["_id"]
            self._update_game_turn(new_messages)
        return new_messages

    def get_messages(self, since_msg_id: str = None) -> list[dict]:
        """
        Retrieve new messages from the game server.
        Note: the "initial_wargame" message will be discarded (last in the list).
        """
        if since_msg_id:
            # Get the last document or documents since a specific ID
            messages = self._get_messages_since_id(since_msg_id)
        else:
            # Retrieve all message documents for the specified wargame.
            messages = self._get_wargame()
        if messages and messages[-1]["_id"] == "initial_wargame":
            messages = messages[:-1]  # remove the initial war game definition message
        return messages

    def _update_game_turn(self, messages: list[dict]):
        # Sync the game's turn number and phase with the last InfoMessage received
        info_messages = list(msg for msg in messages if msg["messageType"] == "InfoMessage")
        if info_messages:
            self.turn_number = info_messages[-1]["gameTurn"]
            self.phase = info_messages[-1]["phase"]

    def _get_wargame(self) -> list[dict] | None:
        try:
            response = requests.get(self.api_endpoint, timeout=5)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            print(f"Request to {self.api_endpoint} failed: {e}")
            return None

    def _get_messages_since_id(self, last_id: str) -> list[dict] | None:
        try:
            response = requests.get(f"{self.api_endpoint}/lastDoc/{last_id}", timeout=5)
            response.raise_for_status()
            return response.json()["data"]
        except requests.exceptions.RequestException as e:
            print(f"Request to {self.api_endpoint} failed: {e}")
            return None

    def get_wargame_last(self) -> dict | None:
        try:
            response = requests.get(f"{self.api_endpoint}/last", timeout=5)
            response.raise_for_status()
            messages = response.json()["data"]
            return messages[0]  # there should only be once message in the returned list
        except requests.exceptions.RequestException as e:
            print(f"Request to {self.api_endpoint} failed: {e}")
            return None

    def send_message(self, message: dict):
        # remove _rev if present
        if "_rev" in message:
            del message["_rev"]
        # setting the message metadata
        timestamp_str = datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        message["details"].update({"timestamp": timestamp_str})
        if "collaboration" in message["details"]:
            # applies to WA messages only
            message["details"]["collaboration"]["lastUpdated"] = timestamp_str
        message["details"].update({"turnNumber": self.turn_number})
        message["_id"] = timestamp_str

        # posting the message to the game
        response = requests.put(self.api_endpoint, json.dumps(message), headers={"Content-Type": "application/json"})
        if not response.ok:
            print(response.status_code)
            print(response.json())

    def send_chat_message(self, text_msg: str):
        msg_chat = MSG_CHAT.copy()
        msg_chat["message"]["content"] = text_msg
        self.send_message(msg_chat)

    def send_WA_message(
        self,
        channel: int,
        threat_id: str,
        weapon_id: int,
        threat_type: str,
        eta_minute: int,
        velocity: int,
        target: int,
    ):
        msg_wa = MSG_WA.copy()
        content = msg_wa["message"]
        content["Title"] = threat_id
        content["Weapon"] = self.MAPPING_WEAPON[weapon_id]

        eta = (datetime.combine(date.today(), self.game_time) + timedelta(minutes=eta_minute)).time()
        content["Threat"] = {
            "Detected type": threat_type,
            "Expected ETA": eta.isoformat("minutes"),
            "ID": threat_id,
            "Ship Targeted": self.MAPPING_SHIP[target],
            "Velocity": velocity,
        }

        # update the target channel
        msg_wa["details"]["channel"] = self.MAPPING_CHANNEL[channel]

        self.send_message(msg_wa)


# Below are the various JSON message templates that are used to communicate with Serge
MSG_MAPPING_SHIPS = {  # placing the two ships on the map with a 100-km range circle
    "_id": "2024-06-06T13:37:33.436Z",
    "details": {
        "channel": "core-mapping",
        "from": {
            "force": "umpire",
            "forceColor": "#FCFBEE",
            "iconURL": "http://localhost:8080/default_img/umpireDefault.png",
            "roleId": "umpire",
            "roleName": "Game Control",
        },
        "messageType": "MappingMessage",
        "timestamp": "2024-06-03T13:37:33",
        "turnNumber": 0,
    },
    "featureCollection": {
        "features": [
            {
                "geometry": {"coordinates": [43.21484211402448, 12.819648833091783], "type": "Point"},
                "properties": {
                    "_type": "MilSymRenderer",
                    "category": "Military",
                    "force": "f-taskforce",
                    "health": 100,
                    "id": "ship-alpha",
                    "label": "Alpha",
                    "phase": "planning",
                    "sidc": "30033020001202031500",
                    "size": "S",
                    "turn": 0,
                },
                "type": "Feature",
            },
            {
                "geometry": {"coordinates": [43.21343663644983, 12.818947918209624], "type": "Point"},
                "properties": {
                    "_type": "MilSymRenderer",
                    "category": "Military",
                    "force": "f-taskforce",
                    "health": 100,
                    "id": "ship-bravo",
                    "label": "Bravo",
                    "phase": "planning",
                    "sidc": "30033020001202031500",
                    "size": "S",
                    "turn": 0,
                },
                "type": "Feature",
            },
            {
                "type": "Feature",
                "properties": {
                    "_type": "CoreRenderer",
                    "color": "#777",
                    "force": "f-taskforce",
                    "id": "feature-range-100",
                    "label": "100km range",
                    "phase": "planning",
                    "turn": 0,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [43.21357045974609, 13.718655567489348],
                            [43.12280602539128, 13.714307694684527],
                            [43.03292547714801, 13.701306428929607],
                            [42.944803788221904, 13.679778400138437],
                            [42.85929820943637, 13.64993323633563],
                            [42.77723966474626, 13.612061448488438],
                            [42.69942444963254, 13.566531504081734],
                            [42.626606324935565, 13.513786123447463],
                            [42.55948909187895, 13.454337841473041],
                            [42.498719725994754, 13.388763885159975],
                            [42.44488213865247, 13.31770042447816],
                            [42.39849162520135, 13.241836259987004],
                            [42.35999004864128, 13.161906015729029],
                            [42.32974179750961, 13.078682909930535],
                            [42.308030546551514, 12.992971179081723],
                            [42.29505683893466, 12.905598233050958],
                            [42.290936499437514, 12.817406620068708],
                            [42.29569987930217, 12.729245880761486],
                            [42.30929192536949, 12.641964369996716],
                            [42.331573058738805, 12.556401124189332],
                            [42.36232084151288, 12.473377849989872],
                            [42.40123240416965, 12.393691107986529],
                            [42.4479276006958, 12.318104762265127],
                            [42.501952853762354, 12.24734276342863],
                            [42.5627856478542, 12.182082329018405],
                            [42.629839624325896, 12.122947581233417],
                            [42.70247022879333, 12.070503697433722],
                            [42.779980858048496, 12.0252516241619],
                            [42.861629450779795, 11.987623400338219],
                            [42.946635463785036, 11.957978129903324],
                            [43.03418717308346, 11.936598638518708],
                            [43.12344923738153, 11.923688843019043],
                            [43.21357045974609, 11.919371856175845],
                            [43.30369168211064, 11.923688843019043],
                            [43.392953746408715, 11.936598638518708],
                            [43.48050545570713, 11.957978129903324],
                            [43.56551146871237, 11.987623400338219],
                            [43.64716006144367, 12.0252516241619],
                            [43.724670690698844, 12.070503697433722],
                            [43.79730129516628, 12.122947581233417],
                            [43.86435527163797, 12.182082329018405],
                            [43.92518806572982, 12.24734276342863],
                            [43.97921331879637, 12.318104762265127],
                            [44.02590851532252, 12.393691107986529],
                            [44.064820077979284, 12.473377849989872],
                            [44.09556786075336, 12.556401124189332],
                            [44.117848994122674, 12.641964369996716],
                            [44.13144104019, 12.729245880761486],
                            [44.13620442005466, 12.817406620068708],
                            [44.13208408055752, 12.905598233050958],
                            [44.11911037294065, 12.992971179081723],
                            [44.097399121982555, 13.078682909930535],
                            [44.06715087085089, 13.161906015729029],
                            [44.02864929429082, 13.241836259987004],
                            [43.9822587808397, 13.31770042447816],
                            [43.928421193497414, 13.388763885159975],
                            [43.86765182761322, 13.454337841473041],
                            [43.80053459455661, 13.513786123447463],
                            [43.72771646985963, 13.566531504081734],
                            [43.649901254745906, 13.612061448488438],
                            [43.5678427100558, 13.64993323633563],
                            [43.48233713127027, 13.679778400138437],
                            [43.394215442344155, 13.701306428929607],
                            [43.3043348941009, 13.714307694684527],
                            [43.21357045974609, 13.718655567489348],
                        ]
                    ],
                },
            },
        ],
        "type": "FeatureCollection",
    },
    "messageType": "MappingMessage",
}
MSG_CHAT = {  # a chat message
    "_id": "2024-06-12T21:59:21.561Z",
    "messageType": "CustomMessage",
    "templateId": "chat",
    "details": {
        "channel": "channel-chat",
        "from": {
            "force": "Taskforce",
            "forceColor": "#3dd0ff",
            "roleId": "ai-assistant",
            "roleName": "AI Assistant",
            "iconURL": "http://localhost:8080/default_img/forceDefault.png",
        },
        "timestamp": "2024-06-12T21:59:21.561Z",
        "privateMessage": "",
        "turnNumber": 0,
    },
    "message": {"content": "<Text content>"},
}
MSG_WA = {  # a weapon assignment message
    "_id": "2024-06-12T22:02:39.113Z",
    "messageType": "CustomMessage",
    "templateId": "WA Message",
    "details": {
        "channel": "channel-wa-alpha",  # the channel corresponds to a ship
        "from": {
            "force": "Taskforce",
            "forceId": "f-taskforce",
            "forceColor": "#3dd0ff",
            "roleName": "AI Assistant",
            "roleId": {
                "forceId": "f-taskforce",
                "forceName": "Taskforce",
                "roleId": "ai-assistant",
                "roleName": "AI Assistant",
            },
            "iconURL": "http://localhost:8080/default_img/forceDefault.png",
        },
        "timestamp": "2024-06-12T22:02:39.113Z",
        "turnNumber": 0,
        "collaboration": {"status": "Pending review", "lastUpdated": "2024-06-12T22:02:39.113Z"},
    },
    "message": {
        "Threat": {
            "Detected type": "ASM",
            "Expected ETA": "15:09",
            "ID": "B01",
            "Ship Targeted": "Ship A",
            "Velocity": 850,
        },
        "Title": "B01",
        "Weapon": "Long Range",
    },
}
