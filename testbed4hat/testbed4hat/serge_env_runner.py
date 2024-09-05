import time
from copy import deepcopy
from typing import Tuple
from warnings import warn

import numpy as np
import pyproj
from pyproj import CRS, Transformer
from shapely.geometry import Point
from shapely.ops import transform

from serge import MSG_MAPPING_SHIPS, SergeGame
from testbed4hat.testbed4hat.messages import WeaponEndMessage
from testbed4hat.testbed4hat.hat_env import HatEnv
from testbed4hat.testbed4hat.hat_env_config import HatEnvConfig
from testbed4hat.testbed4hat.heuristic_agent import HeuristicAgent
from testbed4hat.testbed4hat.utils import compute_pk_ring_radii

THREAT_TEMPLATE = {
    "geometry": {"coordinates": [43.21484211402448, 12.819648833091783], "type": "Point"},
    "properties": {
        "_type": "MilSymRenderer",
        "category": "Military",
        "force": "f-militia",
        "health": 100,
        "id": "threat_id",
        "label": "Threat",
        "phase": "planning",
        "sidc": "30050200001100000005",
        "size": "S",
        "turn": 0,
        "Detected type": "UNK",
        "Expected ETA": "15:09",
        "Ship Targeted": "Ship A",
        "Velocity": [850, 900],
    },
    "type": "Feature",
}

WEAPON_TEMPLATE = {
    "geometry": {"coordinates": [43.21484211402448, 12.819648833091783], "type": "Point"},
    "properties": {
        "_type": "MilSymRenderer",
        "category": "Military",
        "force": "f-taskforce",
        "health": 100,
        "id": "weapon_id",
        "label": "Alpha",
        "phase": "planning",
        "sidc": "30030200001100000205",
        "size": "S",
        "turn": 0,
        "type": "Weapon Type",
        "status": "InTheAir",
        "Launched by": "Ship Name",
        "Threat Targeted": "threat_id",
        "Expected ETA": "15:09",
    },
    "type": "Feature",
}

SUGGESTED_ACTION_TEMPLATE = {  # a weapon assignment message
    "_id": "UNSPECIFIED",
    "messageType": "CustomMessage",
    "templateId": "WA Message",
    "details": {
        "channel": "UNSPECIFIED",  # the channel corresponds to a ship
        "from": {
            "force": "Taskforce",
            "forceId": "f-taskforce",
            "forceColor": "#3dd0ff",
            "roleName": "AI Assistant",
            "roleId": "ai-assistant",
            "iconURL": "http://localhost:8080/default_img/forceDefault.png",
        },
        "timestamp": "UNSPECIFIED",
        "turnNumber": None,
        "collaboration": {"status": "Pending review", "lastUpdated": "UNSPECIFIED"},
    },
    "message": {
        "Threat": {
            "Detected type": "ASM",
            "Expected ETA": "UNSPECIFIED",
            "ID": "UNSPECIFIED",
            "Ship Targeted": "UNSPECIFIED",
            "Velocity": None,
        },
        "Title": "UNSPECIFIED",
        "Weapon": "UNSPECIFIED",
    },
}


def geodesic_point_buffer(lat, lon, m):
    # Azimuthal equidistant projection
    # Adapted from: https://gis.stackexchange.com/questions/121256/creating-a-circle-with-radius-in-metres
    aeqd_proj = CRS.from_proj4(f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0")
    tfmr = Transformer.from_proj(aeqd_proj, aeqd_proj.geodetic_crs)
    buf = Point(0, 0).buffer(m)  # distance in metres
    return transform(tfmr.transform, buf).exterior.coords[:]


def get_pd_polygons(lat, lon):
    low_pk_ring_radius, short_weapon_pk_radius, long_weapon_pk_radius = compute_pk_ring_radii()
    low_pk_ring = geodesic_point_buffer(lat, lon, low_pk_ring_radius)  # in meters
    short_weapon_pk_ring = geodesic_point_buffer(lat, lon, short_weapon_pk_radius)  # in meters
    long_weapon_pk_ring = geodesic_point_buffer(lat, lon, long_weapon_pk_radius)  # in meters

    # convert to serge format
    low_pk_ring = [[list(coord) for coord in low_pk_ring]]
    short_weapon_pk_ring = [[list(coord) for coord in short_weapon_pk_ring]]
    long_weapon_pk_ring = [[list(coord) for coord in long_weapon_pk_ring]]
    return low_pk_ring, short_weapon_pk_ring, long_weapon_pk_ring


class SergeEnvRunner:
    WEAPON_STR_TO_INT = {"Long Range": 0, "Short Range": 1}
    WEAPON_INT_TO_STR = {0: "Long Range", 1: "Short Range"}
    WAIT_TIME_BETWEEN_POLLS = 3

    def __init__(self, game_id: str, server_url: str = "https://serge-inet.herokuapp.com"):
        # todo: log game to local storage?

        # long-lat coords in Serge: [43.21484211402448, 12.819648833091783]
        lat_long_zero = [12.819648833091783, 43.21484211402448]  # The lat-long coordinates of (0, 0) in the sim

        # Note: not confident I know how this works
        self.coordinate_projector = pyproj.Proj(proj="utm", zone=31, ellps="WGS84", preserve_units=True)

        self.cartesian_zero = self.coordinate_projector(*lat_long_zero)

        self.hard_ship_0_location = [-250, -200]
        self.hard_ship_1_location = [250, 150]  # verify okay with Dong

        ship_0_loc_adjusted = [
            self.cartesian_zero[0] + self.hard_ship_0_location[0],
            self.cartesian_zero[1] + self.hard_ship_0_location[1],
        ]
        ship_1_loc_adjusted = [
            self.cartesian_zero[0] + self.hard_ship_1_location[0],
            self.cartesian_zero[1] + self.hard_ship_1_location[1],
        ]

        self.ship_0_lat_long = self.coordinate_projector(*ship_0_loc_adjusted, inverse=True)
        self.ship_1_lat_long = self.coordinate_projector(*ship_1_loc_adjusted, inverse=True)
        self.ship_0_long_lat = [self.ship_0_lat_long[1], self.ship_0_lat_long[0]]
        self.ship_1_long_lat = [self.ship_1_lat_long[1], self.ship_1_lat_long[0]]

        config = HatEnvConfig()
        # set hard-coded game parameters
        config.set_parameter("hard_ship_0_location", self.hard_ship_0_location)
        config.set_parameter("hard_ship_1_location", self.hard_ship_1_location)

        # tentative threat schedule: Should be 10 minutes long, with all threats getting to the ship by the last step
        threat_schedule = {
            10: (0, 1),  # Threat type 1 at second 10 (step 0)
            50: (1, 0),  # Threat type 0 at second 50 (step 0)
            1 * 60 + 10: (1, 0),  # Threat type 0 at 1 min 10 seconds (step 1)
            2 * 60 + 30: (1, 1),  # One of each threat type at 2 min 30 seconds (step 2)
            3 * 60 + 15: (1, 0),  # Threat type 0 at 3 min 15 seconds (step 3)
            4 * 60 + 1: (0, 1),  # Threat type 1 at 4 min 1 second (step 4)
            4 * 60 + 40: (1, 1),  # One of each threat type at 4 min 40 seconds (step 4)
        }
        config.set_parameter("schedule", threat_schedule)
        config.set_parameter("weapon_0_reload_time", 1)
        config.set_parameter("weapon_1_reload_time", 1)
        config.set_parameter("num_ship_0_weapon_0", 10)
        config.set_parameter("num_ship_0_weapon_1", 10)
        config.set_parameter("num_ship_1_weapon_0", 10)
        config.set_parameter("num_ship_1_weapon_1", 10)
        # note that the only difference between threats in the sim is their speed and displayed size
        threat_0_speed = 500.0 * 1000 / 3600  # 500 Km/hr -> m/s
        threat_1_speed = 550.0 * 1000 / 3600  # 550 Km/hr -> m/s
        config.set_parameter("threat_0_speed", threat_0_speed)
        config.set_parameter("threat_1_speed", threat_1_speed)

        min_threat_distance = 30 * 1000  # 30km -> meters
        max_threat_distance = 40 * 1000  # 40km -> meters
        config.set_parameter("min_threat_distance", min_threat_distance)
        config.set_parameter("max_threat_distance", max_threat_distance)

        config.set_parameter("render_env", False)
        # config.set_parameter("verbose", False)

        # Set max time to 12 minutes
        config.set_parameter("max_episode_time_in_seconds", 10 * 60)

        config.set_parameter("seed", 1337)

        out = get_pd_polygons(*lat_long_zero)
        self.low_pk_range_polygon, self.short_weapon_range_polygon, self.long_weapon_range_polygon = out

        self.env_config = config
        self.env = None
        self.obs = None
        self.reward = None
        self.terminated = None
        self.truncated = None
        self.info = None
        self.turn = None
        self.turn_actions = None
        self.ship_features = None
        self.heuristic_agent = None
        self.turns_processed = None

        # serge setup vars
        self.game_id = game_id
        self.url = server_url
        self.serge_game = SergeGame(game_id=game_id, server_url=server_url)  # interface to Serge
        self.ship_0_channel_id = None
        self.ship_1_channel_id = None
        self.ship_0_serge_name = "Alpha"
        self.ship_1_serge_name = "Bravo"
        self.last_adjudication_msg_id: str | None = None

    def _reset_env(self):
        self.obs, self.info = self.env.reset()
        self.terminated = False
        self.truncated = False
        self.turn = 0
        self.turn_actions = []
        self.turns_processed = {0}
        self.heuristic_agent = HeuristicAgent(
            self.env_config.weapon_0_speed,
            self.env_config.weapon_1_speed,
            threshold=0.5,  # arbitrary choice, update as needed for desired performance
            max_actions=4,
        )

    @staticmethod
    def _sim_threat_id_to_serge_id(threat_id: str) -> str:
        return threat_id[len("threat_") :]

    @staticmethod
    def _serge_threat_id_to_sim_id(threat_id: str) -> str:
        return "threat_" + threat_id

    def _convert_wa_message_to_action(self, wa_message) -> Tuple[int, int, str]:
        # # WA message
        # Tuple is (ship_number: int, weapon_type: int, threat_id: str)
        assert wa_message["details"]["channel"] in [self.ship_0_channel_id, self.ship_1_channel_id]  # must be set!
        ship_number = 0 if wa_message["details"]["channel"] == self.ship_0_channel_id else 1
        weapon_type = self.WEAPON_STR_TO_INT[wa_message["message"]["Weapon"]]
        threat_id = self._serge_threat_id_to_sim_id(wa_message["message"]["Threat"]["ID"])
        return ship_number, weapon_type, threat_id

    def _process_action_msg(self, message) -> None:
        # Only action on a "Released" WA message
        if message["details"]["collaboration"]["status"] != "Released":
            return

        action = self._convert_wa_message_to_action(message)

        # We will action messages on a rolling basis, so just add it to the list of actions to send to the env, until
        #   the turn is over.
        self.turn_actions.append(action)

    def _step_environment(self) -> None:
        self.obs, self.reward, self.terminated, self.truncated, self.info = self.env.step(self.turn_actions)
        self.turn_actions = []
        self.turn += 1

    def _sim_xy_to_lat_long(self, x, y):
        # convert to map xy coordinates
        x_adjusted = x + self.cartesian_zero[0]
        y_adjusted = y + self.cartesian_zero[1]

        # convert to Lat-Long
        lat, long = self.coordinate_projector(x_adjusted, y_adjusted, inverse=True)
        return lat, long

    def _make_suggested_action_message(self, action_tuple: tuple) -> dict:
        WA_MSG = deepcopy(SUGGESTED_ACTION_TEMPLATE)
        # Message 'id' is specified in serge_game.send_message()
        # Message 'details.timestamp` specified in serge_game.send_massage()
        # todo: how to specify 'details.collaboration.lastUpdated'?

        assert action_tuple[0] in [0, 1]
        assert action_tuple[1] in [0, 1]
        ship_id = action_tuple[0]
        weapon_type = action_tuple[1]
        threat_id = action_tuple[2]

        WA_MSG["details"]["channel"] = self.ship_0_channel_id if ship_id == 0 else self.ship_1_channel_id
        threat_info = None
        for threat in self.obs["ship_0"]["threats"] + self.obs["ship_1"]["threats"]:
            if threat_id == threat["threat_id"]:
                threat_info = threat
                break
        WA_MSG["message"]["Threat"]["Expected ETA"] = threat_info["estimated_time_of_arrival"]
        WA_MSG["message"]["Threat"]["ID"] = self._sim_threat_id_to_serge_id(threat_info["threat_id"])
        target_ship = int(threat_info["target_ship"])
        assert target_ship in [0, 1]  # ship IDs are 1 indexed
        ship_targeted = self.ship_0_serge_name if target_ship == 0 else self.ship_1_serge_name
        WA_MSG["message"]["Threat"]["Ship Targeted"] = ship_targeted
        speed = np.linalg.norm(threat_info["velocity"])
        WA_MSG["message"]["Threat"]["Velocity"] = str(speed)
        WA_MSG["message"]["Title"] = "Suggested WA"
        WA_MSG["message"]["Weapon"] = self.WEAPON_INT_TO_STR[weapon_type]
        return WA_MSG

    def _send_suggested_actions(self) -> None:
        action = self.heuristic_agent.heuristic_action(self.obs)
        for a in action:
            action_msg = self._make_suggested_action_message(a)
            self.serge_game.send_message(action_msg)

    def _make_threat_dict(self, threat: dict) -> dict:
        threat_dict = deepcopy(THREAT_TEMPLATE)
        threat_x, threat_y = threat["location"]

        # convert to Lat-Long
        threat_lat, threat_long = self._sim_xy_to_lat_long(threat_x, threat_y)
        threat_dict["geometry"]["coordinates"] = [threat_long, threat_lat]  # Serge wants long-lat

        threat_dict["properties"]["id"] = self._sim_threat_id_to_serge_id(threat["threat_id"])
        threat_dict["properties"]["label"] = "Threat " + self._sim_threat_id_to_serge_id(threat["threat_id"])
        threat_dict["properties"]["turn"] = self.turn
        threat_dict["properties"]["Expected ETA"] = str(float(threat["estimated_time_of_arrival"]))
        target_ship = int((threat["target_ship"]))
        threat_dict["properties"]["Ship Targeted"] = "Alpha" if target_ship == 0 else "Bravo"

        threat_dict["properties"]["Long Range PK"] = str(float(threat["weapon_0_kill_probability"]))
        threat_dict["properties"]["Short Range PK"] = str(float(threat["weapon_1_kill_probability"]))
        threat_dict["properties"]["Weapons Assigned"] = threat["weapons_assigned"]
        threat_dict["properties"]["Weapons Assigned PK"] = str([float(t) for t in threat["weapons_assigned_p_kill"]])
        threat_dict["properties"]["Detected type"] = str(threat["threat_type"])

        speed = np.linalg.norm(threat["velocity"])
        threat_dict["properties"]["Velocity"] = str(speed)
        # want weapon assigned type?
        return threat_dict

    def _make_weapon_dict(
        self,
        weapon: dict,
        status: str = None,
    ) -> dict:
        weapon_dict = deepcopy(WEAPON_TEMPLATE)

        ship_id = weapon["ship_id"]
        serge_ship_id = self.ship_0_serge_name if ship_id == 0 else self.ship_1_serge_name
        weapon_x, weapon_y = weapon["location"]

        # convert to Lat-Long
        weapon_lat, weapon_long = self._sim_xy_to_lat_long(weapon_x, weapon_y)
        weapon_dict["geometry"]["coordinates"] = [weapon_long, weapon_lat]  # serge wants long-lat
        weapon_dict["properties"]["id"] = weapon["weapon_id"]
        weapon_dict["properties"]["label"] = weapon["weapon_id"]
        weapon_dict["properties"]["turn"] = self.turn
        weapon_dict["properties"]["type"] = self.WEAPON_INT_TO_STR[weapon["weapon_type"]]
        # use the default status "InTheAir" if no status is provided
        if status is not None:
            # the weapon is spent
            weapon_dict["properties"]["status"] = status
            weapon_dict["properties"]["health"] = 0
            weapon_dict["properties"]["sidc"] = "30030240001100000212"
        weapon_dict["properties"]["Launched by"] = serge_ship_id
        weapon_dict["properties"]["Expected ETA"] = weapon["time_left"]
        weapon_dict["properties"]["Threat Targeted"] = weapon["target_id"]
        weapon_dict["properties"]["PK"] = weapon["probability_of_kill"]
        return weapon_dict

    def _build_ship_features(self):
        # constructing the mapping message from the template
        message = deepcopy(MSG_MAPPING_SHIPS)
        message["featureCollection"]["features"][0]["geometry"]["coordinates"] = self.ship_0_long_lat
        message["featureCollection"]["features"][1]["geometry"]["coordinates"] = self.ship_1_long_lat

        ship_0_weapon_0_inventory = self.obs["ship_0"]["inventory"]["weapon_0_inventory"]
        ship_0_weapon_1_inventory = self.obs["ship_0"]["inventory"]["weapon_1_inventory"]
        ship_1_weapon_0_inventory = self.obs["ship_1"]["inventory"]["weapon_0_inventory"]
        ship_1_weapon_1_inventory = self.obs["ship_1"]["inventory"]["weapon_1_inventory"]
        message["featureCollection"]["features"][0]["properties"]["Long Range ammo"] = ship_0_weapon_0_inventory
        message["featureCollection"]["features"][0]["properties"]["Short Range ammo"] = ship_0_weapon_1_inventory
        message["featureCollection"]["features"][1]["properties"]["Long Range ammo"] = ship_1_weapon_0_inventory
        message["featureCollection"]["features"][1]["properties"]["Short Range ammo"] = ship_1_weapon_1_inventory

        # make range polygon features
        range_dict = message["featureCollection"]["features"][2]
        low_range_dict = deepcopy(range_dict)
        low_range_dict["properties"]["label"] = "Low Range"
        low_range_dict["properties"]["id"] = "feature-range-low"
        low_range_dict["properties"]["color"] = "#777"
        low_range_dict["geometry"]["coordinates"] = self.low_pk_range_polygon
        short_range_dict = deepcopy(range_dict)
        short_range_dict["properties"]["label"] = "Short Range"
        short_range_dict["properties"]["id"] = "feature-range-short"
        short_range_dict["properties"]["color"] = "#666"
        short_range_dict["geometry"]["coordinates"] = self.short_weapon_range_polygon
        long_range_dict = deepcopy(range_dict)
        long_range_dict["properties"]["label"] = "Long Range"
        long_range_dict["properties"]["id"] = "feature-range-long"
        long_range_dict["properties"]["color"] = "#555"
        long_range_dict["geometry"]["coordinates"] = self.long_weapon_range_polygon

        self.ship_features = [
            message["featureCollection"]["features"][0],  # Ship 0
            message["featureCollection"]["features"][1],  # Ship 1
            low_range_dict,  # Range circle: Low
            short_range_dict,  # Range circle: Short
            long_range_dict,  # Range circle: Long
        ]

    def _build_step_message(self) -> dict:
        # Convert the observation to a Serge message and send it to Serge

        # get threats
        threat_ids = set()
        threats = []
        for threat in self.obs["ship_0"]["threats"]:
            threat_ids.add(threat["threat_id"])
            threat_dict = self._make_threat_dict(threat)
            threats.append(threat_dict)

        for threat in self.obs["ship_1"]["threats"]:
            threat_id = threat["threat_id"]
            if threat_id not in threat_ids:
                threat_ids.add(threat["threat_id"])
                threat_dict = self._make_threat_dict(threat)
                threats.append(threat_dict)

        # get weapons
        weapons = []
        weapon_ids = set()
        for weapon in self.obs["ship_0"]["weapons"]:
            weapon_ids.add(weapon["weapon_id"])
            weapon_dict = self._make_weapon_dict(weapon)
            weapons.append(weapon_dict)

        # get any weapons seen by Ship 1 but NOT ship 0 (both ships see weapons launched by each other)
        for weapon in self.obs["ship_1"]["weapons"]:
            weapon_id = weapon["weapon_id"]
            if weapon_id not in weapon_ids:
                weapon_ids.add(weapon["weapon_id"])
                weapon_dict = self._make_weapon_dict(weapon)
                weapons.append(weapon_dict)

        # process game events captured in messages
        for message in self.obs["messages"]:
            if isinstance(message, WeaponEndMessage):
                weapon_dict = self._make_weapon_dict(message.weapon, "Hit" if message.destroyed_target else "Missed")
                weapons.append(weapon_dict)

        step_message = deepcopy(MSG_MAPPING_SHIPS)

        if not self.ship_features:
            # should only occur once, on the first step
            self._build_ship_features()

        # update ship weapon inventories
        ship_features = self.ship_features
        ship_0_weapon_0_inventory = self.obs["ship_0"]["inventory"]["weapon_0_inventory"]
        ship_0_weapon_1_inventory = self.obs["ship_0"]["inventory"]["weapon_1_inventory"]
        ship_1_weapon_0_inventory = self.obs["ship_1"]["inventory"]["weapon_0_inventory"]
        ship_1_weapon_1_inventory = self.obs["ship_1"]["inventory"]["weapon_1_inventory"]
        ship_features[0]["properties"]["Long Range ammo"] = ship_0_weapon_0_inventory
        ship_features[0]["properties"]["Short Range ammo"] = ship_0_weapon_1_inventory
        ship_features[1]["properties"]["Long Range ammo"] = ship_1_weapon_0_inventory
        ship_features[1]["properties"]["Short Range ammo"] = ship_1_weapon_1_inventory

        step_message["featureCollection"]["features"] = ship_features + threats + weapons

        return step_message

    def _update_serge_state_of_the_world(self) -> None:
        """
        Send a message to the serge server to update the serge state. (Separate from sim update, which occurs when
        entering planning phase).
        """
        mapping_msg = self._build_step_message()
        self.serge_game.send_message(mapping_msg)

    def _process_custom_message(self, message: dict) -> None:
        """
        Processes a custom message from Serge
        """
        msg_template = message["templateId"]
        if msg_template == "WA Message":
            # Store the message in the queue to process when the adjudication phase starts
            self._process_action_msg(message)

    def _send_obs_messages(self):
        launch_messages = self.obs["launched"]
        fail_messages = self.obs["failed"]
        other_messages = self.obs["messages"]
        # Send launched messages
        for launch in launch_messages:
            text = "Weapon Launched! \nWeapon info:\n"
            for k, v in launch.items():
                text += f"{k}: {v}\n"
            self.serge_game.send_chat_message(text)
        # Send failed messages
        for fail in fail_messages:
            text = "Miss! \nWeapon info:\n"
            for k, v in fail.items():
                text += f"{k}: {v}\n"
            self.serge_game.send_chat_message(text)
        # Send the rest of the messages
        for other in other_messages:
            self.serge_game.send_chat_message(other.to_string())

    def _process_adjudication_phase(self) -> None:
        """
        Processes all the actions that were sent during the turn
        """
        # 1. Generate the array of actions from WA messages (already done in self.process_custom_message)
        # 2. Execute the queued actions and get the new observations
        self._step_environment()
        # 3. Send serge the new sim state
        self._update_serge_state_of_the_world()
        # 4. Send serge sim-generated messages
        self._send_obs_messages()
        # 5. Generate and send new WA messages from AI
        self._send_suggested_actions()

    def _read_serge_game_settings(self):
        game_message = self.serge_game.get_wargame_last()
        game_data = game_message["data"]
        # find out the channels for the ships (for WA messages)
        if "channels" in game_data and "channels" in game_data["channels"]:
            for channel in game_data["channels"]["channels"]:
                if channel["name"] == self.ship_0_serge_name:
                    self.ship_0_channel_id = channel["uniqid"]
                if channel["name"] == self.ship_1_serge_name:
                    self.ship_1_channel_id = channel["uniqid"]

    def _wait_until_next_adjudication_phase(self) -> str:
        while True:
            # Retrieve new messages from the server
            new_messages = self.serge_game.get_new_messages()

            # looking for an InfoMessage with phase == "adjudication"
            for message in new_messages:
                if message["messageType"] == "InfoMessage" and message["phase"] == "adjudication":
                    return message["_id"]  # return the message ID to mark where this turn ends

            # Wait for a few seconds before checking for new messages again
            time.sleep(self.WAIT_TIME_BETWEEN_POLLS)

    def _process_messages_in_the_last_turn(self, adjudication_msg_id: str) -> str | None:
        # Retrieved messages afresh from Serge since the last turn
        new_messages = self.serge_game.get_messages(since_msg_id=self.last_adjudication_msg_id)

        while new_messages:
            # Process one message at a time
            message = new_messages.pop(0)
            message_type = message["messageType"]
            if message_type == "CustomMessage":
                # Process custom messages (Chat, WA)
                self._process_custom_message(message)
            elif message_type == "InfoMessage":
                msg_id = message["_id"]
                msg_turn_number = message["gameTurn"]
                if message["phase"] == "adjudication":
                    if msg_id == self.last_adjudication_msg_id:
                        continue  # skip the last adjudication message, we've already processed it

                    # process the adjudication phase
                    self.last_adjudication_msg_id = msg_id  # remember where we are
                    if msg_turn_number not in self.turns_processed:
                        self._process_adjudication_phase()
                        self.turns_processed.add(self.turn)
                    # we've done with this turn, stop processing any more messages
                    break
            elif message_type == "MappingMessage":
                # ignoring mapping messages
                continue
            else:  # skipping all other message types
                warn(f"Unexpected message type received! Type: {message_type}")

        # if there are still more messages that haven't been processed, look out for a new adjudication phase
        adjudication_messages = filter(
            lambda m: m["messageType"] == "InfoMessage" and m["phase"] == "adjudication", new_messages
        )
        try:
            return next(adjudication_messages)["_id"]  # we will process until this adjudication message the next time
        except StopIteration:
            return None

    def run(self):
        self.env = HatEnv(self.env_config)
        running = True

        # initialize a new game
        self._reset_env()
        self._read_serge_game_settings()
        self._update_serge_state_of_the_world()

        while running:
            adjudication_msg_id = self._wait_until_next_adjudication_phase()
            while adjudication_msg_id:
                # more than one turn may have passed, we keep processing until seeing no more adjudication messages
                adjudication_msg_id = self._process_messages_in_the_last_turn(adjudication_msg_id)

            if self.terminated or self.truncated:
                running = False
                self.serge_game.send_chat_message("Simulation terminated.")


if __name__ == "__main__":
    game_id = "wargame-m0p9azmu"
    runner = SergeEnvRunner(game_id=game_id)
    runner.run()
