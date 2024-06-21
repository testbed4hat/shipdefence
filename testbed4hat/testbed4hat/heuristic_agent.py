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

from typing import Union, Tuple

from .pk_table import get_pk
from .utils import distance, get_weapon_launch_info


class HeuristicAgent:
    """
    A heuristic agent for the HAT simulation environment. The agent uses observation information about the currently
    observed threats, the current weapons in flight, and the probabilities of success for weapons to choose a set of
    actions to take at a given step. Weapon/threat assignments are prioritized based on probability of success for the
    different types of weapons eliminating the threat, and the distance the threat is to the ship.
    """
    def __init__(self, weapon_0_speed: float, weapon_1_speed: float, threshold: float = 0.35, max_actions: int = 10):
        """
        Initialize heuristic agent.
        :param weapon_0_speed: (float) Speed of weapon type 0.
        :param weapon_1_speed: (float) Speed of weapon type 1.
        :param threshold: (float) Value in [0, 1] defining a probabilistic threshold under which actions will not be
            taken. Note that the weight used by the heuristic agent is not a perfect/true probability, but thinking
            about the action weight as a probability of the intersection of two events (will destroy the ship if not
            eliminated and the weapon will eliminate the threat) is a reasonable mental model for what this value is
            thresholding.
        :param max_actions: (int) The maximum number of actions to provide to the environment for a given step.
        """
        self.weapon_0_speed = weapon_0_speed
        self.weapon_1_speed = weapon_1_speed
        self.threshold = threshold
        self.ship_1_key = "ship_1"
        self.ship_2_key = "ship_2"
        self.ship_1_idx = 0
        self.ship_2_idx = 1

        self.max_threat_dist = 70_000
        self.max_urgency_dist = 10_000
        self.max_actions = max_actions

    def _get_ship_weapon_choice(self, ship_threat, ship_location, ship_idx, ship_inventory) \
            -> Union[Tuple[int, int, str, float], None]:
        """
        For a given ship, choose a weapon most likely to eliminate the threat. If the likelihood of eliminating the
        threat is too low, based on the <threshold> value, do not choose an action. Similarly, if the inventory of a
        weapon is 0, do not try to use that weapon.
        :param ship_threat: (dict) The observation information for the threat in question.
        :param ship_location: (tuple) The location of the ship in question.
        :param ship_idx: (int) The index of the current ship (for creating the action).
        :param ship_inventory: (dict) The inventory observation for the current ship.
        :return: (ship index, weapon type, threat ID, action weight) if action weight is above the threshold, None
            otherwise.
        """
        # Returns None if no good choices (threshold and inventory may block)
        threat_distance = ship_threat["distance"]
        threat_location = ship_threat["location"]
        threat_velocity = ship_threat["velocity"]

        if threat_distance > self.max_urgency_dist:
            ship_threat_urgency = 1 - threat_distance / self.max_threat_dist
        else:
            ship_threat_urgency = 1.0

        weapon_0_intercept_info = get_weapon_launch_info(threat_location, ship_location, threat_velocity,
                                                         self.weapon_0_speed)
        weapon_1_intercept_info = get_weapon_launch_info(threat_location, ship_location, threat_velocity,
                                                         self.weapon_1_speed)

        intercept_point_weapon_0 = weapon_0_intercept_info["intercept_point"]
        intercept_point_weapon_1 = weapon_1_intercept_info["intercept_point"]
        dist_to_intercept_weapon_0 = distance(ship_location, intercept_point_weapon_0)
        dist_to_intercept_weapon_1 = distance(ship_location, intercept_point_weapon_1)

        ship_weapon_0_pk = get_pk(dist_to_intercept_weapon_0, 0, ship_threat["threat_type"])
        ship_weapon_1_pk = get_pk(dist_to_intercept_weapon_1, 1, ship_threat["threat_type"])
        ship_weapon_0_weight = ship_threat_urgency * ship_weapon_0_pk
        ship_weapon_1_weight = ship_threat_urgency * ship_weapon_1_pk

        if ship_weapon_0_weight > self.threshold or ship_weapon_1_weight > self.threshold:
            if ship_weapon_0_weight > ship_weapon_1_weight and ship_inventory['weapon_0_inventory'] > 0:
                return ship_idx, 0, ship_threat["threat_id"], ship_weapon_0_weight
            elif ship_inventory['weapon_1_inventory'] > 0:
                return ship_idx, 1, ship_threat["threat_id"], ship_weapon_1_weight

    def heuristic_action(self, observation: dict):
        """
        Strategy is to launch the most likely weapons to destroy the most urgent threats, up to some set max number of
        per turn. Only launch a weapon at a threat if no weapon has been launched against it yet. Decisions are made
        for both ships.
        :param observation: (dict) The observation from the HAT environment.
        :return: (list) List of actions to take at this step.
        """

        ship_1_location = observation[self.ship_1_key]['location']
        ship_2_location = observation[self.ship_2_key]['location']

        ship_1_threat_obs = observation[self.ship_1_key]['threats']
        ship_2_threat_obs = observation[self.ship_2_key]['threats']

        ship_1_threat_dict = dict([(t["threat_id"], t) for t in ship_1_threat_obs])
        ship_2_threat_dict = dict([(t["threat_id"], t) for t in ship_2_threat_obs])
        my_threat_obs = (ship_1_threat_obs
                         + [s for s in ship_2_threat_obs if s['threat_id'] not in ship_1_threat_dict.keys()])
        ship_1_weapon_obs = observation[self.ship_1_key]['weapons']
        ship_2_weapon_obs = observation[self.ship_2_key]['weapons']

        my_weapon_obs = ship_1_weapon_obs + ship_2_weapon_obs
        targeted_threats = [w['target_id'] for w in my_weapon_obs]

        actions = []
        for threat in my_threat_obs:
            if threat["threat_id"] in targeted_threats:
                continue
            weapon_options = []
            if threat["threat_id"] in ship_1_threat_dict:
                ship_threat = ship_1_threat_dict[threat["threat_id"]]
                weapon = self._get_ship_weapon_choice(ship_threat, ship_1_location, self.ship_1_idx,
                                                      observation[self.ship_1_key]['inventory'])
                if weapon is not None:
                    weapon_options.append(weapon)
            if threat["threat_id"] in ship_2_threat_dict:
                ship_threat = ship_2_threat_dict[threat["threat_id"]]
                weapon = self._get_ship_weapon_choice(ship_threat, ship_2_location, self.ship_2_idx,
                                                      observation[self.ship_2_key]['inventory'])
                if weapon is not None:
                    weapon_options.append(weapon)
            if len(weapon_options) == 0:
                continue
            elif len(weapon_options) == 1:
                actions.append(weapon_options[0])
            elif len(weapon_options) == 2:
                w = weapon_options[0] if weapon_options[0][-1] > weapon_options[1][-1] else weapon_options[1]
                actions.append(w)
            else:
                raise RuntimeError(f"Agent has more weapon options to consider than anticipated (> 2):\n"
                                   f"{weapon_options}")

        actions_sorted = sorted(actions, key=lambda action: action[-1], reverse=True)
        return [a[:3] for a in actions_sorted[:self.max_actions]]
