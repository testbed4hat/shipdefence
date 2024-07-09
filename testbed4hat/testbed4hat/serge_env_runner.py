from testbed4hat.testbed4hat.hat_env import HatEnv
from testbed4hat.testbed4hat.hat_env_config import HatEnvConfig
from testbed4hat.testbed4hat.utils import compute_pk_ring_radii
from typing import Union, Tuple
import requests
from serge import MSG_MAPPING_SHIPS, MSG_WA, MSG_CHAT, SergeGame
import pyproj
from pyproj import CRS, Transformer
from shapely.geometry import Point
from shapely.ops import transform
from datetime import datetime

THREAT_TEMPLATE = {
    "geometry": {"coordinates": [43.21484211402448, 12.819648833091783], "type": "Point"},
    "properties": {
        "_type": "Threat",
        "category": "Military",
        "force": "UNK",
        "health": 100,
        "id": "threat_id",
        "label": "UNK",
        "phase": "UNK",
        "sidc": "UNK",
        "size": "UNK",
        "turn": 0,
    },
    "Threat": {
        "Detected type": "ASM",
        "Expected ETA": "15:09",
        "ID": "B01",
        "Ship Targeted": "Ship A",
        "Velocity": 850,
    },
    "Title": "B01",
    "Weapon": "Long Range",
    "type": "Feature",

}

WEAPON_TEMPLATE = {
    "geometry": {"coordinates": [43.21484211402448, 12.819648833091783], "type": "Point"},
    "properties": {
        "_type": "Weapon",
        "category": "Military",
        "force": "UNK",
        "health": 100,
        "id": "weapon_id",
        "label": "UNK",
        "phase": "UNK",
        "sidc": "UNK",
        "size": "UNK",
        "turn": 0,
    },
    "Weapon": {
        "Expected ETA": "15:09",
        "ID": "B01",
        "Ship Targeted": "Ship A",
        "Velocity": 850,
    },
    "Title": "B01",
    "Threat": "Long Range",
    "type": "Feature",
}


def geodesic_point_buffer(lat, lon, m):
    # Azimuthal equidistant projection
    # Adapted from: https://gis.stackexchange.com/questions/121256/creating-a-circle-with-radius-in-metres
    aeqd_proj = CRS.from_proj4(
        f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0")
    tfmr = Transformer.from_proj(aeqd_proj, aeqd_proj.geodetic_crs)
    buf = Point(0, 0).buffer(m)  # distance in metres
    return transform(tfmr.transform, buf).exterior.coords[:]


def get_pd_polygons(lat, lon):
    low_pk_ring_radius, short_weapon_pk_radius, long_weapon_pk_radius = compute_pk_ring_radii()
    low_pk_ring = geodesic_point_buffer(lat, lon, low_pk_ring_radius)  # in meters
    short_weapon_pk_ring = geodesic_point_buffer(lat, lon, low_pk_ring_radius)  # in meters
    long_weapon_pk_ring = geodesic_point_buffer(lat, lon, low_pk_ring_radius)  # in meters
    return low_pk_ring, short_weapon_pk_ring, long_weapon_pk_ring


class SergeEnvRunner:
    WEAPON_STR_TO_INT = {"Long Range": 0, "Short Range": 1}

    def __init__(self, game_id: str, server_url: str = "https://serge-inet.herokuapp.com"):
        # todo: log game to local storage?
        lat_long_zero = [43.21484211402448, 12.819648833091783]  # The lat-long coordinates of (0, 0) in the sim

        # Note: not confident I know how this works
        self.coordinate_projector = pyproj.Proj(proj='utm', zone=31, ellps='WGS84', preserve_units=True)

        self.cartesian_zero = self.coordinate_projector(*lat_long_zero)

        self.hard_ship_1_location = [-250, -200]
        self.hard_ship_2_location = [250, 150]  # verify okay with Dong

        ship_1_loc_adjusted = [self.cartesian_zero[0] + self.hard_ship_1_location[0],
                               self.cartesian_zero[1] + self.hard_ship_1_location[1]]
        ship_2_loc_adjusted = [self.cartesian_zero[0] + self.hard_ship_2_location[0],
                               self.cartesian_zero[1] + self.hard_ship_2_location[1]]

        self.ship_1_lat_long = self.coordinate_projector(*ship_1_loc_adjusted, inverse=True)
        self.ship_2_lat_long = self.coordinate_projector(*ship_2_loc_adjusted, inverse=True)

        config = HatEnvConfig()
        # set hard-coded game parameters
        config.set_parameter("hard_ship_1_location", self.hard_ship_1_location)
        config.set_parameter("hard_ship_2_location", self.hard_ship_2_location)

        # tentative threat schedule
        threat_schedule = {
            59: (0, 1),
            2 * 60 - 1: (1, 0),
            3 * 60 - 30: (1, 1)
        }
        config.set_parameter("schedule", threat_schedule)
        config.set_parameter("weapon_0_reload_time", 1)
        config.set_parameter("weapon_1_reload_time", 1)
        config.set_parameter("num_ship_1_weapon_0", 10)
        config.set_parameter("num_ship_1_weapon_1", 10)
        config.set_parameter("num_ship_2_weapon_0", 10)
        config.set_parameter("num_ship_2_weapon_1", 10)

        # Set max time to 12 minutes
        config.set_parameter("max_episode_time_in_seconds", 12 * 60)

        config.set_parameter("seed", 1337)

        # send to Serge?
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

        # serge setup vars
        self.game_id = game_id
        self.url = server_url
        self.serge_game = SergeGame(game_id=game_id, server_url=server_url)

        # serge state variables
        self.current_game_state: list[dict] | None = None
        self.wargame_last: list[dict] | None = None

        # bools
        self.should_get_wargame: bool = True
        self.should_get_wargame_last: bool = True
        self.should_send_message: bool = False
        self.should_send_chat_message: bool = False
        self.should_send_WA_message: bool = False

    def reset_function_list(self):
        self.function_list = list(self.function_map.keys())

    def set_current_game_state(self, data: list[dict] | None = None):
        if data is not None:
            self.current_game_state = data
            return True
        else:
            # failed to update game state
            return False

    def set_wargame_last(self, data: list[dict] | None = None):
        if data is not None:
            self.wargame_last = data
            return True
        else:
            # failed to update game state
            return False

    def _reset_env(self):
        self.obs, self.info = self.env.reset()
        self.terminated = False
        self.truncated = False
        self.turn = 0

    def _listen_for_message(self) -> Union[dict, None]:
        # todo: listen for messages. If message found, parse and return
        return None

    def _convert_wa_message_to_action(self, wa_message) -> Tuple[int, int, str]:
        # # WA message
        # Tuple is (ship_number: int, weapon_type: int, threat_id: str)
        ship_number = 0 if wa_message['channel'] == self.serge_game.MAPPING_SHIP[1] else 1  # todo: verify!
        weapon_type = self.WEAPON_STR_TO_INT[wa_message['message']["Weapon"]]  # todo: verify!
        threat_id = wa_message['message']["Title"]  # todo: verify!
        return ship_number, weapon_type, threat_id

    def _process_action_msg(self, message) -> None:
        action = self._convert_wa_message_to_action(message)

        '''
        We will action messages on a rolling basis, so just add it to the list of actions to send to the env, until 
        the turn is over.
        '''
        self.turn_actions.append(action)

    def _step_environment(self) -> None:
        self.obs, self.reward, self.terminated, self.truncated, self.info = self.env.step(self.turn_actions)
        self.turn += 1

    def sim_xy_to_lat_long(self, x, y):
        # convert to map xy coordinates
        x_adjusted = x + self.cartesian_zero[0]
        y_adjusted = y + self.cartesian_zero[1]

        # convert to Lat-Long
        lat, long = self.coordinate_projector(x_adjusted, y_adjusted, inverse=True)
        return lat, long

    def _make_threat_dict(self, threat: dict) -> dict:
        threat_dict = THREAT_TEMPLATE.copy()
        threat_x, threat_y = threat['location']

        # convert to Lat-Long
        threat_lat, threat_long = self.sim_xy_to_lat_long(threat_x, threat_y)
        threat_dict['geometry']['coordinates'] = [threat_lat, threat_long]

        threat_dict['id'] = threat['threat_id']
        threat_dict['turn'] = self.turn
        threat_dict['Threat']["Expected ETA"] = threat['estimated_time_of_arrival']
        threat_dict['Threat']["ID"] = threat['threat_id']
        threat_dict['Threat']["Ship Targeted"] = threat['target_ship']
        threat_dict['Threat']["Velocity"] = threat['velocity']
        threat_dict['Title'] = threat['threat_id']
        threat_dict['Weapon'] = "Long Range" if threat['threat_id'] == 0 else "Short Range"
        threat_dict['Long Range PK'] = threat['weapon_0_kill_probability']
        threat_dict['Short Range PK'] = threat['weapon_1_kill_probability']
        threat_dict['Weapons Assigned'] = threat['weapons_assigned']
        threat_dict['Weapons Assigned PK'] = threat['weapons_assigned_p_kill']
        # want weapon assigned type?
        return threat_dict

    def _make_weapon_dict(self, weapon: dict) -> dict:
        weapon_dict = WEAPON_TEMPLATE.copy()
        weapon_x, weapon_y = weapon['location']

        # convert to Lat-Long
        weapon_lat, weapon_long = self.sim_xy_to_lat_long(weapon_x, weapon_y)
        weapon_dict['geometry']['coordinates'] = [weapon_lat, weapon_long]
        weapon_dict['id'] = weapon['weapon_id']
        weapon_dict['turn'] = self.turn
        weapon_dict['Weapon']["Expected ETA"] = weapon['time_left']
        weapon_dict['Weapon']["ID"] = weapon['weapon_id']
        weapon_dict['Weapon']["Threat Targeted"] = weapon['target_id']
        weapon_dict['Title'] = weapon['weapon_id']
        weapon_dict['PK'] = weapon['probability_of_kill']
        return weapon_dict

    def _send_step_message(self) -> None:
        # Convert the observation to a Serge message and send it to Serge
        ship_1_weapon_0_inventory = self.obs['ship_1']['inventory']["weapon_0_inventory"]
        ship_1_weapon_1_inventory = self.obs['ship_1']['inventory']["weapon_1_inventory"]
        ship_2_weapon_0_inventory = self.obs['ship_2']['inventory']["weapon_0_inventory"]
        ship_2_weapon_1_inventory = self.obs['ship_2']['inventory']["weapon_1_inventory"]

        threat_ids = set()
        threats = []
        for threat in self.obs['ship_1']['threats']:
            threat_ids.add(threat['threat_id'])
            threat_dict = self._make_threat_dict(threat)
            threats.append(threat_dict)

        for threat in self.obs['ship_2']['threats']:
            threat_id = threat['threat_id']
            if threat_id not in threat_ids:
                threat_ids.add(threat['threat_id'])
                threat_dict = self._make_threat_dict(threat)
                threats.append(threat_dict)

        weapons = []
        weapon_ids = set()
        for weapon in self.obs['ship_1']['weapons']:
            weapon_ids.add(weapon['weapon_id'])
            weapon_dict = self._make_weapon_dict(weapon)
            weapons.append(weapon_dict)

        for weapon in self.obs['ship_2']['weapons']:
            weapon_id = weapon['weapon_id']
            if weapon_id not in weapon_ids:
                weapon_ids.add(weapon['weapon_id'])
                weapon_dict = self._make_weapon_dict(weapon)
                weapons.append(weapon_dict)

        step_message = MSG_MAPPING_SHIPS.copy()
        step_message['FeatureCollection']['features'] = threats + weapons
        step_message['details']['turn_number'] = self.turn
        step_message['details']['timestamp'] = datetime.now().strftime("%Y-%M-%dT%H:%m:%S")

        # Note: not sure where to put these yet...
        step_message['Ship 1 Long Range Inventory'] = ship_1_weapon_0_inventory
        step_message['Ship 1 Short Range Inventory'] = ship_1_weapon_1_inventory
        step_message['Ship 2 Long Range Inventory'] = ship_2_weapon_0_inventory
        step_message['Ship 2 Short Range Inventory'] = ship_2_weapon_1_inventory

        self.serge_game.send_message(step_message)

    def run(self):
        self.env = HatEnv(self.env_config)

        running = True
        reset = True

        while running:
            if reset:
                self._reset_env()
                reset = False

                # send start game message with updated information
                start_msg = MSG_MAPPING_SHIPS.copy()
                start_msg["featureCollection"]["features"][0]["geometry"]["coordinates"] = self.ship_1_lat_long
                start_msg["featureCollection"]["features"][1]["geometry"]["coordinates"] = self.ship_2_lat_long

                # make range polygon features
                range_dict = start_msg["featureCollection"]["features"][2]
                low_range_dict = range_dict.copy()
                low_range_dict["label"] = "Low Range"
                low_range_dict["id"] = "feature-range-low"
                low_range_dict["color"] = "#777"
                low_range_dict["geometry"]["coordinates"] = self.low_pk_range_polygon
                short_range_dict = range_dict.copy()
                short_range_dict["label"] = "Short Range"
                short_range_dict["id"] = "feature-range-short"
                short_range_dict["color"] = "#666"
                short_range_dict["geometry"]["coordinates"] = self.short_weapon_range_polygon
                long_range_dict = range_dict.copy()
                long_range_dict["label"] = "Long Range"
                long_range_dict["id"] = "feature-range-long"
                long_range_dict["color"] = "#555"
                long_range_dict["geometry"]["coordinates"] = self.long_weapon_range_polygon

                start_msg["featureCollection"] = [
                    start_msg["featureCollection"]["features"][0],
                    start_msg["featureCollection"]["features"][1],
                    low_range_dict,
                    short_range_dict,
                    long_range_dict
                ]

                self.serge_game.send_message(start_msg)

            # if self.should_get_wargame:
            #     data = self.serge_game.get_wargame()
            #     self.set_current_game_state(data)
            #
            # if self.should_get_wargame_last:
            #     data = self.serge_game.get_wargame_last()
            #     self.set_wargame_last(data)
            #
            # if self.should_send_message:
            #     # self.serge_game.send_message({})
            #     pass
            #
            # if self.should_send_chat_message:
            #     # self.serge_game.send_chat_message("")
            #     pass
            #
            # if self.should_send_WA_message:
            #     # self.serge_game.send_WA_message()
            #     pass

            msg = self._listen_for_message()

            if msg:
                if msg["templateId"] == "WA Message":  # Action message case (assign weapons to threats)
                    self._process_action_msg(msg)

                elif msg["templateId"] == "InfoMessage":  # Not a defined message yet, but a case for end turn
                    self._step_environment()
                    self._send_step_message()

                # not doing this?
                # elif msg["templateId"] == "Reset Message":  # Not a defined message yet, but a case for sim reset
                #     reset = True

                elif msg["templateId"] == "Terminate Message":  # Not a defined message yet, but a case for end game
                    running = False

                # todo: additional message types?

            if self.terminated or self. truncated:
                running = False


if __name__ == '__main__':
    game_id = "Testbed4HAT-template-lxcd9mgw"
    runner = SergeEnvRunner(game_id=game_id)
    runner.run()
