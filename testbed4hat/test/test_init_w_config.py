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
import tempfile
import unittest

from testbed4hat.hat_env import HatEnv
from testbed4hat.hat_env_config import HatEnvConfig


class TestInitWithConfig(unittest.TestCase):
    def setUp(self):

        # define a config with different parameters than the default
        self.config_json_data = {
            "seed": 48,
            "seconds_per_timestep": 61,
            "weapon_0_speed": 137.2,
            "weapon_1_speed": 193.9,
            "weapon_0_reload_time": 18,
            "weapon_1_reload_time": 9,
            "num_ship_1_weapon_0": 7,
            "num_ship_1_weapon_1": 6,
            "num_ship_2_weapon_0": 12,
            "num_ship_2_weapon_1": 13,
            "min_distance_between_ships": 1389,
            "max_distance_between_ships": 5208,
            "wasted_weapon_reward": -0.0104355,
            "max_episode_time_in_seconds": 548,
            "verbose": False,
            "render_env": False,
            "zoom": 0.99,
            "screen_width": 1500,
            "screen_height": 1300,
            "threat_0_base_size": 253,
            "threat_1_base_size": 171,
            "threat_0_color": [254, 1, 1],
            "threat_1_color": [252, 162, 2],
            "draw_threat_spawn_region": True,
            "weapon_0_base_size": 103,
            "weapon_1_base_size": 130,
            "weapon_0_color": [121, 122, 123],
            "weapon_1_color": [251, 192, 3],
            "ship_base_length": 593,
            "ship_base_width": 233,
            "ship_1_color": [7, 250, 1],
            "ship_2_color": [1, 2, 235],
            "threat_0_kill_radius": 999,
            "threat_1_kill_radius": 998,
            "threat_0_speed": 112.,
            "threat_1_speed": 143.,
            "threat_0_kill_prob": 0.85,
            "threat_1_kill_prob": 0.75,
            "min_threat_distance": 55555,
            "max_threat_distance": 77777,
            "schedule": {100: (1, 1), 200: (0, 1), 300: (1, 0)}
        }

        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.temp_file.name, 'w') as f:
            json.dump(self.config_json_data, f)

    def test_load_config_run_env(self):

        config = HatEnvConfig(self.temp_file.name)
        self.environment = HatEnv(config)
        self.environment.reset()  # Reset environment so ships are defined

        self.assertEqual(self.environment.seed, self.config_json_data['seed'])
        self.assertEqual(self.environment.seconds_per_timestep, int(self.config_json_data['seconds_per_timestep']))
        self.assertEqual(self.environment.weapon_0_speed, self.config_json_data['weapon_0_speed'])
        self.assertEqual(self.environment.weapon_1_speed, self.config_json_data['weapon_1_speed'])
        self.assertEqual(self.environment.weapon_0_reload_time, self.config_json_data['weapon_0_reload_time'])
        self.assertEqual(self.environment.weapon_1_reload_time, self.config_json_data['weapon_1_reload_time'])
        self.assertEqual(self.environment.num_ship_1_weapon_0, self.config_json_data['num_ship_1_weapon_0'])
        self.assertEqual(self.environment.num_ship_1_weapon_1, self.config_json_data['num_ship_1_weapon_1'])
        self.assertEqual(self.environment.num_ship_2_weapon_0, self.config_json_data['num_ship_2_weapon_0'])
        self.assertEqual(self.environment.num_ship_2_weapon_1, self.config_json_data['num_ship_2_weapon_1'])

        self.assertEqual(self.environment.min_distance_between_ships,
                         self.config_json_data['min_distance_between_ships'])
        self.assertEqual(self.environment.max_distance_between_ships,
                         self.config_json_data['max_distance_between_ships'])
        self.assertEqual(self.environment.wasted_weapon_reward, self.config_json_data['wasted_weapon_reward'])
        self.assertEqual(self.environment.max_episode_time_in_seconds,
                         self.config_json_data['max_episode_time_in_seconds'])
        self.assertEqual(self.environment.verbose, self.config_json_data['verbose'])
        self.assertEqual(self.environment.render_env, self.config_json_data['render_env'])
        self.assertEqual(self.environment.zoom, self.config_json_data['zoom'])
        self.assertEqual(self.environment.screen_width, self.config_json_data['screen_width'])
        self.assertEqual(self.environment.screen_height, self.config_json_data['screen_height'])
        self.assertEqual(self.environment.threat_0_size,
                         self.config_json_data['threat_0_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.threat_1_size,
                         self.config_json_data['threat_1_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.threat_0_color, self.config_json_data['threat_0_color'])
        self.assertEqual(self.environment.threat_1_color, self.config_json_data['threat_1_color'])
        self.assertEqual(self.environment.draw_threat_spawn_region, self.config_json_data['draw_threat_spawn_region'])
        self.assertEqual(self.environment.weapon_0_size,
                         self.config_json_data['weapon_0_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.weapon_1_size,
                         self.config_json_data['weapon_1_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.weapon_0_color, self.config_json_data['weapon_0_color'])
        self.assertEqual(self.environment.weapon_1_color, self.config_json_data['weapon_1_color'])
        self.assertEqual(self.environment.ship_length,
                         self.config_json_data['ship_base_length'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.ship_width,
                         self.config_json_data['ship_base_width'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.ship_1_color, self.config_json_data['ship_1_color'])
        self.assertEqual(self.environment.ship_2_color, self.config_json_data['ship_2_color'])
        self.assertEqual(self.environment.threat_0_kill_radius, self.config_json_data['threat_0_kill_radius'])
        self.assertEqual(self.environment.threat_1_kill_radius, self.config_json_data['threat_1_kill_radius'])
        self.assertEqual(self.environment.threat_0_speed, self.config_json_data['threat_0_speed'])
        self.assertEqual(self.environment.threat_1_speed, self.config_json_data['threat_1_speed'])
        self.assertEqual(self.environment.threat_0_kill_prob, self.config_json_data['threat_0_kill_prob'])
        self.assertEqual(self.environment.threat_1_kill_prob, self.config_json_data['threat_1_kill_prob'])
        self.assertEqual(self.environment.min_threat_distance, self.config_json_data['min_threat_distance'])
        self.assertEqual(self.environment.max_threat_distance, self.config_json_data['max_threat_distance'])
        self.assertEqual(self.environment.schedule, self.config_json_data['schedule'])

        obs, reward, terminated, truncated, info = self.environment.step([])

    def test_dict_config_run_env(self):

        config = HatEnvConfig(self.config_json_data)
        self.environment = HatEnv(config)
        self.environment.reset()  # Reset environment so ships are defined

        self.assertEqual(self.environment.seed, self.config_json_data['seed'])
        self.assertEqual(self.environment.seconds_per_timestep, int(self.config_json_data['seconds_per_timestep']))
        self.assertEqual(self.environment.weapon_0_speed, self.config_json_data['weapon_0_speed'])
        self.assertEqual(self.environment.weapon_1_speed, self.config_json_data['weapon_1_speed'])
        self.assertEqual(self.environment.weapon_0_reload_time, self.config_json_data['weapon_0_reload_time'])
        self.assertEqual(self.environment.weapon_1_reload_time, self.config_json_data['weapon_1_reload_time'])
        self.assertEqual(self.environment.num_ship_1_weapon_0, self.config_json_data['num_ship_1_weapon_0'])
        self.assertEqual(self.environment.num_ship_1_weapon_1, self.config_json_data['num_ship_1_weapon_1'])
        self.assertEqual(self.environment.num_ship_2_weapon_0, self.config_json_data['num_ship_2_weapon_0'])
        self.assertEqual(self.environment.num_ship_2_weapon_1, self.config_json_data['num_ship_2_weapon_1'])

        self.assertEqual(self.environment.min_distance_between_ships,
                         self.config_json_data['min_distance_between_ships'])
        self.assertEqual(self.environment.max_distance_between_ships,
                         self.config_json_data['max_distance_between_ships'])
        self.assertEqual(self.environment.wasted_weapon_reward, self.config_json_data['wasted_weapon_reward'])
        self.assertEqual(self.environment.max_episode_time_in_seconds,
                         self.config_json_data['max_episode_time_in_seconds'])
        self.assertEqual(self.environment.verbose, self.config_json_data['verbose'])
        self.assertEqual(self.environment.render_env, self.config_json_data['render_env'])
        self.assertEqual(self.environment.zoom, self.config_json_data['zoom'])
        self.assertEqual(self.environment.screen_width, self.config_json_data['screen_width'])
        self.assertEqual(self.environment.screen_height, self.config_json_data['screen_height'])
        self.assertEqual(self.environment.threat_0_size,
                         self.config_json_data['threat_0_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.threat_1_size,
                         self.config_json_data['threat_1_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.threat_0_color, self.config_json_data['threat_0_color'])
        self.assertEqual(self.environment.threat_1_color, self.config_json_data['threat_1_color'])
        self.assertEqual(self.environment.draw_threat_spawn_region, self.config_json_data['draw_threat_spawn_region'])
        self.assertEqual(self.environment.weapon_0_size,
                         self.config_json_data['weapon_0_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.weapon_1_size,
                         self.config_json_data['weapon_1_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.weapon_0_color, self.config_json_data['weapon_0_color'])
        self.assertEqual(self.environment.weapon_1_color, self.config_json_data['weapon_1_color'])
        self.assertEqual(self.environment.ship_length,
                         self.config_json_data['ship_base_length'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.ship_width,
                         self.config_json_data['ship_base_width'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.ship_1_color, self.config_json_data['ship_1_color'])
        self.assertEqual(self.environment.ship_2_color, self.config_json_data['ship_2_color'])
        self.assertEqual(self.environment.threat_0_kill_radius, self.config_json_data['threat_0_kill_radius'])
        self.assertEqual(self.environment.threat_1_kill_radius, self.config_json_data['threat_1_kill_radius'])
        self.assertEqual(self.environment.threat_0_speed, self.config_json_data['threat_0_speed'])
        self.assertEqual(self.environment.threat_1_speed, self.config_json_data['threat_1_speed'])
        self.assertEqual(self.environment.threat_0_kill_prob, self.config_json_data['threat_0_kill_prob'])
        self.assertEqual(self.environment.threat_1_kill_prob, self.config_json_data['threat_1_kill_prob'])
        self.assertEqual(self.environment.min_threat_distance, self.config_json_data['min_threat_distance'])
        self.assertEqual(self.environment.max_threat_distance, self.config_json_data['max_threat_distance'])
        self.assertEqual(self.environment.schedule, self.config_json_data['schedule'])

        obs, reward, terminated, truncated, info = self.environment.step([])

    def test_default_config_run_env(self):

        config = HatEnvConfig()
        self.environment = HatEnv(config)
        self.environment.reset()  # Reset environment so ships are defined

        self.assertEqual(self.environment.seed, self.config_json_data['seed'])
        self.assertEqual(self.environment.seconds_per_timestep, int(self.config_json_data['seconds_per_timestep']))
        self.assertEqual(self.environment.weapon_0_speed, self.config_json_data['weapon_0_speed'])
        self.assertEqual(self.environment.weapon_1_speed, self.config_json_data['weapon_1_speed'])
        self.assertEqual(self.environment.weapon_0_reload_time, self.config_json_data['weapon_0_reload_time'])
        self.assertEqual(self.environment.weapon_1_reload_time, self.config_json_data['weapon_1_reload_time'])
        self.assertEqual(self.environment.num_ship_1_weapon_0, self.config_json_data['num_ship_1_weapon_0'])
        self.assertEqual(self.environment.num_ship_1_weapon_1, self.config_json_data['num_ship_1_weapon_1'])
        self.assertEqual(self.environment.num_ship_2_weapon_0, self.config_json_data['num_ship_2_weapon_0'])
        self.assertEqual(self.environment.num_ship_2_weapon_1, self.config_json_data['num_ship_2_weapon_1'])

        self.assertEqual(self.environment.min_distance_between_ships,
                         self.config_json_data['min_distance_between_ships'])
        self.assertEqual(self.environment.max_distance_between_ships,
                         self.config_json_data['max_distance_between_ships'])
        self.assertEqual(self.environment.wasted_weapon_reward, self.config_json_data['wasted_weapon_reward'])
        self.assertEqual(self.environment.max_episode_time_in_seconds,
                         self.config_json_data['max_episode_time_in_seconds'])
        self.assertEqual(self.environment.verbose, self.config_json_data['verbose'])
        self.assertEqual(self.environment.render_env, self.config_json_data['render_env'])
        self.assertEqual(self.environment.zoom, self.config_json_data['zoom'])
        self.assertEqual(self.environment.screen_width, self.config_json_data['screen_width'])
        self.assertEqual(self.environment.screen_height, self.config_json_data['screen_height'])
        self.assertEqual(self.environment.threat_0_size,
                         self.config_json_data['threat_0_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.threat_1_size,
                         self.config_json_data['threat_1_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.threat_0_color, self.config_json_data['threat_0_color'])
        self.assertEqual(self.environment.threat_1_color, self.config_json_data['threat_1_color'])
        self.assertEqual(self.environment.draw_threat_spawn_region, self.config_json_data['draw_threat_spawn_region'])
        self.assertEqual(self.environment.weapon_0_size,
                         self.config_json_data['weapon_0_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.weapon_1_size,
                         self.config_json_data['weapon_1_base_size'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.weapon_0_color, self.config_json_data['weapon_0_color'])
        self.assertEqual(self.environment.weapon_1_color, self.config_json_data['weapon_1_color'])
        self.assertEqual(self.environment.ship_length,
                         self.config_json_data['ship_base_length'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.ship_width,
                         self.config_json_data['ship_base_width'] / self.environment.coordinate_size_reduction)
        self.assertEqual(self.environment.ship_1_color, self.config_json_data['ship_1_color'])
        self.assertEqual(self.environment.ship_2_color, self.config_json_data['ship_2_color'])
        self.assertEqual(self.environment.threat_0_kill_radius, self.config_json_data['threat_0_kill_radius'])
        self.assertEqual(self.environment.threat_1_kill_radius, self.config_json_data['threat_1_kill_radius'])
        self.assertEqual(self.environment.threat_0_speed, self.config_json_data['threat_0_speed'])
        self.assertEqual(self.environment.threat_1_speed, self.config_json_data['threat_1_speed'])
        self.assertEqual(self.environment.threat_0_kill_prob, self.config_json_data['threat_0_kill_prob'])
        self.assertEqual(self.environment.threat_1_kill_prob, self.config_json_data['threat_1_kill_prob'])
        self.assertEqual(self.environment.min_threat_distance, self.config_json_data['min_threat_distance'])
        self.assertEqual(self.environment.max_threat_distance, self.config_json_data['max_threat_distance'])
        self.assertEqual(self.environment.schedule, self.config_json_data['schedule'])

        obs, reward, terminated, truncated, info = self.environment.step([])


if __name__ == '__main__':
    unittest.main()
