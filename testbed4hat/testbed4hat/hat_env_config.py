# Copyright 2024 The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
#
# Licensed under the 3-Clause BSD License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from typing import Union, Any

from .wave_generator import WaveGenerator, DEFAULT_THREAT_0_SPEED, DEFAULT_THREAT_1_SPEED


class HatEnvConfig:
    """Configurate object of HAT environment"""
    SECONDS_PER_TIMESTEP_RANGE = (1, 60 * 60)
    WASTED_REWARD_RANGE = (-1, 0)
    TARGET_HIT_REWARD_RANGE = (0, 5)
    ZOOM_RANGE = (0.5, 5)
    SCREEN_SIZE_RANGE = (400, 2000)
    THREAT_BASE_SIZE_RANGE = (150, 300)
    WEAPON_BASE_SIZE_RANGE = (50, 150)
    SHIP_BASE_SIZE_RANGE = (200, 800)
    COLOR_RANGE = (0, 255)
    MAX_TIME_RANGE = (5 * 60, 60 * 60)
    HARD_SHIP_LOCATION_RANGE = (-1000, 1000)  # in meters
    FONT_SIZE_RANGE = (12, 32)

    PARAM_DESCRIPTION = {
        "config": "Dictionary with HAT environment configuration parameters as key-value pairs, or string path to a "
                  "json file in the same format.",
        "seed": "The seed of the random number generator.",
        "seconds_per_timestep": "Number of seconds to simulate for each environment step.",
        "weapon_0_speed": "The speed of weapon 0.",
        "weapon_1_speed": "The speed of weapon 1.",
        "weapon_0_reload_time":
            "Number of seconds for weapon 0 to reload. The weapon cannot be launched during the "
            "reload period.",
        "weapon_1_reload_time":
            "Number of seconds for weapon 1 to reload. The weapon cannot be launched during the "
            "reload period.",
        "num_ship_0_weapon_0": "Total number of weapon 0 on ship 1.",
        "num_ship_0_weapon_1": "Total number of weapon 1 on ship 1.",
        "num_ship_1_weapon_0": "Total number of weapon 0 on ship 2.",
        "num_ship_1_weapon_1": "Total number of weapon 1 on ship 2.",
        "min_distance_between_ships": "The minimum distance between the two ship locations.",
        "max_distance_between_ships": "The maximum distance between the two ship locations.",
        "hard_ship_0_location": "Force ship 1 to be located a this point (instead of random generation)",
        "hard_ship_1_location": "Force ship 2 to be located a this point (instead of random generation)",
        "wasted_weapon_reward": "The reward returned by the environment for each wasted weapon. A "
                                "weapon is considered 'wasted' if the threat it targeted was "
                                "destroyed before the weapon hit it",
        "target_hit_reward": "The reward returned by the environment for eliminating a threat with a weapon.",
        "max_episode_time_in_seconds": "The total time represented in the simulation (not real-time).",
        "verbose": "Print optional information about the environment, including warnings.",
        "render_env": "Whether to render the environment using PyGame or not.",
        "zoom": "How much to zoom in to the environment during rendering. "
                "Values less than 1 zoom out rather than in.",
        "screen_width": "The width of the screen in pixels.",
        "screen_height": "The height of the screen in pixels.",
        "threat_0_base_size": "Base size of the threat 0 in meters.",
        "threat_1_base_size": "Base size of the threat 1 in meters.",
        "threat_0_color": "Threat 0 color.",
        "threat_1_color": "Threat 1 color.",
        "draw_threat_spawn_region": "Draw a transparent region designating where threats spawn.",
        "weapon_0_base_size": "Base weapon 0 size in meters.",
        "weapon_1_base_size": "Base weapon 1 size in meters.",
        "weapon_0_color": "Weapon 0 color.",
        "weapon_1_color": "Weapon 1 color.",
        "ship_base_length": "The base width of the ship in meters.",
        "ship_base_width": "The base height of the ship in meters.",
        "ship_0_color": "Ship 1 color.",
        "ship_1_color": "Ship 2 color.",
        "font_size": "The font size in for threat visualization.",
        "font_color": "The color of the font for threat visualization.",
        "display_threat_ids": "Whether to display threat IDs when rendering or not.",
        "threat_0_kill_radius": "Radius around ships where threat 0 is effective.",
        "threat_1_kill_radius": "Radius around ships where threat 1 is effective.",
        "threat_0_speed": "Speed of threat 0.",
        "threat_1_speed": "Speed of threat 1.",
        "threat_0_kill_prob": "Probability of threat 0 destroying a ship when in the effective range.",
        "threat_1_kill_prob": "Probability of threat 1 destroying a ship when in the effective range.",
        "min_threat_distance": "The minimum distance a threat can spawn from point (0, 0).",
        "max_threat_distance": "The maximum distance a threat can spawn from point (0, 0).",
        "schedule": "When, and what kind of, threats spawn in the environment."
    }

    PARAM_TYPES = {
        "config": (dict, None),
        "seed": int,
        "seconds_per_timestep": int,
        "weapon_0_speed": float,
        "weapon_1_speed": float,
        "weapon_0_reload_time": int,
        "weapon_1_reload_time": int,
        "num_ship_0_weapon_0": int,
        "num_ship_0_weapon_1": int,
        "num_ship_1_weapon_0": int,
        "num_ship_1_weapon_1": int,
        "min_distance_between_ships": (int, float),
        "max_distance_between_ships": (int, float),
        "wasted_weapon_reward": float,
        "target_hit_reward": float,
        "max_episode_time_in_seconds": int,
        "hard_ship_0_location": (None, tuple, list),
        "hard_ship_1_location": (None, tuple, list),
        "verbose": bool,
        "render_env": bool,
        "zoom": float,
        "screen_width": int,
        "screen_height": int,
        "threat_0_base_size": int,
        "threat_1_base_size": int,
        "threat_0_color": tuple,
        "threat_1_color": tuple,
        "draw_threat_spawn_region": bool,
        "weapon_0_base_size": int,
        "weapon_1_base_size": int,
        "weapon_0_color": tuple,
        "weapon_1_color": tuple,
        "ship_base_length": int,
        "ship_base_width": int,
        "ship_0_color": tuple,
        "ship_1_color": tuple,
        "font_size": int,
        "font_color": tuple,
        "display_threat_ids": bool,
        "threat_0_kill_radius": (float, int),
        "threat_1_kill_radius": (float, int),
        "threat_0_speed": (float, int),
        "threat_1_speed": (float, int),
        "threat_0_kill_prob": float,
        "threat_1_kill_prob": float,
        "min_threat_distance": (float, int),
        "max_threat_distance": (float, int),
        "schedule": (str, dict)
    }

    def __init__(self, config: Union[str, dict] = None):
        self.config = config
        # Defaults
        self.seed = 0
        self.seconds_per_timestep = 60
        self.weapon_0_speed = 7.5 * 1_000 / 60  # 7.5 km/min -> m/s
        self.weapon_1_speed = 9.0 * 1_000 / 60  # 9.0 km/min -> m/s
        self.weapon_0_reload_time = 15
        self.weapon_1_reload_time = 10
        self.num_ship_0_weapon_0 = 10
        self.num_ship_0_weapon_1 = 10
        self.num_ship_1_weapon_0 = 10
        self.num_ship_1_weapon_1 = 10
        self.min_distance_between_ships = 1000  # in meters
        self.max_distance_between_ships = 5000  # in meters
        self.hard_ship_0_location = None
        self.hard_ship_1_location = None
        self.wasted_weapon_reward = -0.01
        self.target_hit_reward = 2.0
        self.max_episode_time_in_seconds = 25 * 60
        self.verbose = True

        # render parameters
        self.render_env = True
        self.zoom = 1
        self.screen_width = 1600
        self.screen_height = 1200
        self.threat_0_base_size = 200
        self.threat_1_base_size = 150
        self.threat_0_color = (255, 0, 0)  # red
        self.threat_1_color = (255, 165, 0)  # orange
        self.draw_threat_spawn_region = False

        self.weapon_0_base_size = 115
        self.weapon_1_base_size = 115
        self.weapon_0_color = (128, 128, 128)  # gray
        self.weapon_1_color = (255, 192, 0)  # golden yellow

        self.ship_base_length = 600
        self.ship_base_width = 200
        self.ship_0_color = (0, 255, 0)  # green
        self.ship_1_color = (0, 0, 255)  # blue

        self.font_size = 18
        self.font_color = (0, 0, 0)  # black
        self.display_threat_ids = True

        # generator parameters
        self.threat_0_kill_radius = 1000
        self.threat_1_kill_radius = 1000
        self.threat_0_speed = DEFAULT_THREAT_0_SPEED
        self.threat_1_speed = DEFAULT_THREAT_1_SPEED
        self.threat_0_kill_prob = 0.95
        self.threat_1_kill_prob = 0.95
        self.min_threat_distance = 50_000  # in meters
        self.max_threat_distance = 70_000  # in meters
        self.schedule = "random"  # See wave_generator.py for viable options

        # load config options if pass
        if self.config is not None:
            if isinstance(config, str):
                with open(config, 'r') as f:
                    self.config = json.load(f)

                if isinstance(self.config['schedule'], dict):
                    typed_dict = {}
                    for k, v in self.config['schedule'].items():
                        typed_dict[int(k)] = tuple(v)
                    self.config['schedule'] = typed_dict

            self.__dict__.update(self.config)

        self.validate()

    def to_dict(self):
        return vars(self).copy()

    def to_json(self, file_path: str):
        data = self.to_dict()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def set_parameter(self, parameter: str, value: Any):
        """
        Set a parameter in the config, checking if the parameter is valid and raising an exception if not.
        :param parameter: (str) parameter name
        :param value: (Any) parameter value
        """
        if parameter not in self.__dict__.keys():
            raise ValueError(f"Parameter {parameter} is not defined")
        self.__dict__[parameter] = value

    def description(self):
        """Print a text description of this object"""
        PARAMS_WITH_RANGES = {"seconds_per_timestep": self.SECONDS_PER_TIMESTEP_RANGE,
                              "wasted_weapon_reward": self.WASTED_REWARD_RANGE,
                              "target_hit_reward": self.TARGET_HIT_REWARD_RANGE,
                              "zoom": self.ZOOM_RANGE,
                              "screen_width": self.SCREEN_SIZE_RANGE,
                              "screen_height": self.SCREEN_SIZE_RANGE,
                              "threat_0_base_size": self.THREAT_BASE_SIZE_RANGE,
                              "threat_1_base_size": self.THREAT_BASE_SIZE_RANGE,
                              "weapon_0_base_size": self.WEAPON_BASE_SIZE_RANGE,
                              "weapon_1_base_size": self.WEAPON_BASE_SIZE_RANGE,
                              "max_episode_time_in_seconds": self.MAX_TIME_RANGE,
                              "hard_ship_0_location": self.HARD_SHIP_LOCATION_RANGE,
                              "hard_ship_1_location": self.HARD_SHIP_LOCATION_RANGE,
                              "font_size": self.FONT_SIZE_RANGE,
                              }
        print("The configuration object for the HatEnv environment. The configuration parameters are as follows:")
        print()
        for k, v in self.__dict__.items():
            print(f"Parameter: {k}")
            print(f"\tType: {self.PARAM_TYPES[k]}")
            print(f"\tCurrent value: {v}")
            print(f"\tDescription: {self.PARAM_DESCRIPTION[k]}")
            if "color" in k:
                print(f"\tNote: Colors are 3-tuples with values between 0 and 255")
            if k == "schedule":
                print(f"\tValid string inputs are: {WaveGenerator.SCHEDULE_STRING_OPTIONS}")
                print(f"\tNote: Schedule keys are integers representing the second the threats are launched, and values"
                      f"\n\tare 2-tuples with values of 0 or 1. The first index is whether to launch a threat of type "
                      f"\n\t0, and the second index is whether to launch a threat of type 1, respectively.")
            if k in PARAMS_WITH_RANGES:
                print(f"\tRange: {PARAMS_WITH_RANGES[k]}")

    def _validate_color(self, color):
        assert isinstance(color, (tuple, list)) and len(color) == 3
        assert all([isinstance(p, int) for p in color])
        assert all([self.COLOR_RANGE[0] <= p <= self.COLOR_RANGE[1] for p in color])

    def validate(self):
        if self.config is not None:
            assert isinstance(self.config, dict)
        assert isinstance(self.seed, int)
        assert isinstance(self.seconds_per_timestep, int)
        assert self.SECONDS_PER_TIMESTEP_RANGE[0] <= self.seconds_per_timestep <= self.SECONDS_PER_TIMESTEP_RANGE[1]
        assert isinstance(self.weapon_0_speed, float) and 0 < self.weapon_0_speed
        assert isinstance(self.weapon_1_speed, float) and 0 < self.weapon_1_speed
        assert isinstance(self.weapon_0_reload_time, int) and 0 <= self.weapon_0_reload_time
        assert isinstance(self.weapon_1_reload_time, int) and 0 <= self.weapon_1_reload_time
        assert isinstance(self.num_ship_0_weapon_0, int) and 0 <= self.num_ship_0_weapon_0
        assert isinstance(self.num_ship_0_weapon_1, int) and 0 <= self.num_ship_0_weapon_1
        assert isinstance(self.num_ship_1_weapon_0, int) and 0 <= self.num_ship_1_weapon_0
        assert isinstance(self.num_ship_1_weapon_1, int) and 0 <= self.num_ship_1_weapon_1
        assert isinstance(self.min_distance_between_ships, (int, float)) and 0 < self.min_distance_between_ships
        assert isinstance(self.max_distance_between_ships, (int, float)) and 0 < self.max_distance_between_ships
        assert self.hard_ship_0_location is None or isinstance(self.hard_ship_0_location, (tuple, list))
        if self.hard_ship_0_location is not None:
            for coord in self.hard_ship_0_location:
                assert self.HARD_SHIP_LOCATION_RANGE[0] <= coord <= self.HARD_SHIP_LOCATION_RANGE[1]
        assert self.hard_ship_1_location is None or isinstance(self.hard_ship_1_location, (tuple, list))
        if self.hard_ship_1_location is not None:
            for coord in self.hard_ship_1_location:
                assert self.HARD_SHIP_LOCATION_RANGE[0] <= coord <= self.HARD_SHIP_LOCATION_RANGE[1]
        assert isinstance(self.wasted_weapon_reward, float)
        assert self.WASTED_REWARD_RANGE[0] <= self.wasted_weapon_reward <= self.WASTED_REWARD_RANGE[1]
        assert isinstance(self.target_hit_reward, float)
        assert self.TARGET_HIT_REWARD_RANGE[0] <= self.target_hit_reward <= self.TARGET_HIT_REWARD_RANGE[1]
        assert isinstance(self.max_episode_time_in_seconds, int)
        assert self.MAX_TIME_RANGE[0] <= self.max_episode_time_in_seconds <= self.MAX_TIME_RANGE[1]
        assert isinstance(self.verbose, bool)

        # render parameters
        assert isinstance(self.render_env, bool)
        assert isinstance(self.zoom, (int, float))
        assert self.ZOOM_RANGE[0] <= self.zoom <= self.ZOOM_RANGE[1]  # Keep zoom reasonable
        assert isinstance(self.screen_width, int)
        assert self.SCREEN_SIZE_RANGE[0] < self.screen_width <= self.SCREEN_SIZE_RANGE[1]
        assert isinstance(self.screen_height, int)
        assert self.SCREEN_SIZE_RANGE[0] < self.screen_height <= self.SCREEN_SIZE_RANGE[1]
        assert isinstance(self.threat_0_base_size, int)
        assert self.THREAT_BASE_SIZE_RANGE[0] <= self.threat_0_base_size <= self.THREAT_BASE_SIZE_RANGE[1]
        assert isinstance(self.threat_1_base_size, int)
        assert self.THREAT_BASE_SIZE_RANGE[0] <= self.threat_1_base_size <= self.THREAT_BASE_SIZE_RANGE[1]
        assert isinstance(self.draw_threat_spawn_region, bool)
        self._validate_color(self.threat_0_color)
        self._validate_color(self.threat_1_color)

        assert isinstance(self.weapon_0_base_size, int)
        assert self.WEAPON_BASE_SIZE_RANGE[0] <= self.weapon_0_base_size <= self.WEAPON_BASE_SIZE_RANGE[1]
        assert isinstance(self.weapon_1_base_size, int)
        assert self.WEAPON_BASE_SIZE_RANGE[0] <= self.weapon_1_base_size <= self.WEAPON_BASE_SIZE_RANGE[1]
        self._validate_color(self.weapon_0_color)
        self._validate_color(self.weapon_1_color)

        assert isinstance(self.ship_base_length, int)
        assert isinstance(self.ship_base_width, int)
        assert self.SHIP_BASE_SIZE_RANGE[0] <= self.ship_base_width <= self.SHIP_BASE_SIZE_RANGE[1]
        assert self.SHIP_BASE_SIZE_RANGE[0] <= self.ship_base_length <= self.SHIP_BASE_SIZE_RANGE[1]
        assert self.ship_base_width <= self.ship_base_length - 200  # keep reasonable proportions
        self._validate_color(self.ship_0_color)
        self._validate_color(self.ship_1_color)

        assert self.FONT_SIZE_RANGE[0] <= self.font_size <= self.FONT_SIZE_RANGE[1]
        self._validate_color(self.font_color)
        assert isinstance(self.display_threat_ids, bool)

        # generator parameters
        assert isinstance(self.threat_0_kill_radius, (float, int)) and 0 < self.threat_0_kill_radius
        assert isinstance(self.threat_1_kill_radius, (float, int)) and 0 < self.threat_1_kill_radius
        assert isinstance(self.threat_0_speed, (float, int)) and 0 < self.threat_0_speed
        assert isinstance(self.threat_1_speed, (float, int)) and 0 < self.threat_0_speed
        assert isinstance(self.threat_0_kill_prob, float) and 0.0 <= self.threat_0_kill_prob <= 1.0
        assert isinstance(self.threat_1_kill_prob, float) and 0.0 <= self.threat_0_kill_prob <= 1.0
        assert isinstance(self.min_threat_distance, (float, int)) and 0 < self.min_threat_distance
        assert isinstance(self.max_threat_distance, (float, int)) and 0 < self.max_threat_distance
        assert (isinstance(self.schedule, str) and self.schedule in WaveGenerator.SCHEDULE_STRING_OPTIONS
                or isinstance(self.schedule, dict))
        if isinstance(self.schedule, dict):
            for key, value in self.schedule.items():
                assert isinstance(key, int) and isinstance(value, tuple)
                assert value == (0, 1) or value == (1, 0) or value == (1, 1)
