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


import os

from testbed4hat.testbed4hat.hat_env import HatEnv
from testbed4hat.testbed4hat.hat_env_config import HatEnvConfig
from testbed4hat.testbed4hat.heuristic_agent import HeuristicAgent


def run_scenario():
    """
    Run the scenario intended to run with Serge, but with Python only. In other words, run the config intended to
    be used for the Serge experiments.
    """
    config = HatEnvConfig()
    hard_ship_0_location = [-250, -200]
    hard_ship_1_location = [250, 150]  # verify okay with Dong

    # set hard-coded game parameters
    config.set_parameter("hard_ship_0_location", hard_ship_0_location)
    config.set_parameter("hard_ship_1_location", hard_ship_1_location)

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
    config.set_parameter("num_ship_0_weapon_0", 20)
    config.set_parameter("num_ship_0_weapon_1", 20)
    config.set_parameter("num_ship_1_weapon_0", 20)
    config.set_parameter("num_ship_1_weapon_1", 20)
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
    config.set_parameter("verbose", False)

    # Set max time to 12 minutes
    config.set_parameter("max_episode_time_in_seconds", 10 * 60)

    config.set_parameter("seed", 1337)
    config.validate()

    serge_config_file = "serge_scenario_config.json"
    if not os.path.isfile(serge_config_file):
        config.to_json(serge_config_file)

    # set config to render and print info for this script
    config.set_parameter("render_env", True)
    config.set_parameter("verbose", True)

    env = HatEnv(config)
    heuristic_agent = HeuristicAgent(config.weapon_0_speed, config.weapon_1_speed, max_actions=15)

    obs, info = env.reset()

    max_steps = 30
    safety_counter = 0

    done = False
    while not done and safety_counter < max_steps:
        safety_counter += 1

        actions = heuristic_agent.heuristic_action(obs)
        obs, reward, terminated, truncated, info = env.step(actions)
        done = terminated or truncated

        print(f"Launched: {obs['launched']}")
        print(f"Failed Launches: {obs['failed']}")
        print(f"Messages: {obs['messages']}")
        print("Step:", safety_counter, "-"*50)


if __name__ == '__main__':
    run_scenario()
