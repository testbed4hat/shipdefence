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

from testbed4hat.hat_env_config import HatEnvConfig
from testbed4hat.hat_env import HatEnv
import argparse
import numpy as np
import time
from testbed4hat.heuristic_agent import HeuristicAgent


def run_scenario(path_to_config: str = None):
    if path_to_config is not None:
        with open(path_to_config, 'r') as f:
            config_dict = json.load(f)
    else:
        # define custom config here
        config_dict = {"zoom": 1.2}
    config = HatEnvConfig(config_dict)

    config.set_parameter("seed", np.random.randint(10000))
    config.set_parameter("num_ship_0_weapon_0", 50)
    config.set_parameter("num_ship_0_weapon_1", 50)
    config.set_parameter("num_ship_1_weapon_0", 50)
    config.set_parameter("num_ship_1_weapon_1", 50)
    config.set_parameter("weapon_0_reload_time", 3)
    config.set_parameter("weapon_1_reload_time", 3)
    config.validate()

    env = HatEnv(config)
    terminated = False
    truncated = False
    max_steps = 30
    safety_counter = 0

    agent = HeuristicAgent(config.weapon_0_speed, config.weapon_1_speed, max_actions=15)

    obs, info = env.reset()
    while not (terminated or truncated) and safety_counter < max_steps:
        safety_counter += 1
        action = agent.heuristic_action(obs)
        obs, reward, terminated, truncated, info = env.step(action)

        print(f"Launched: {obs['launched']}")
        print(f"Failed Launches: {obs['failed']}")
        print(f"Messages: {obs['messages']}")
        print(safety_counter, "-"*50)


if __name__ == '__main__':
    run_scenario()
