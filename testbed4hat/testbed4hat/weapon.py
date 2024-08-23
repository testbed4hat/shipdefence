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

import copy
from typing import Tuple, Union

import numpy as np

from .pk_table import get_pk
from .threat import Threat
from .utils import distance, get_weapon_launch_info


class Weapon:
    def __init__(
        self,
        ship_id: int,
        ship_location: Tuple[float, float],
        ship_orientation: float,
        weapon_speed: float,
        threat: Threat,
        weapon_type: int,
        weapon_id: str,
        rng: np.random.RandomState,
    ):
        """
        A weapon for neutralizing threats.
        :param ship_id: (int) Ship of origin.
        :param ship_location: (float, float) Ship of origin location in meters.
        :param ship_orientation: Ship of origin orientation, in degrees. (Not currently used, as PK does not depend on
            orientation in this version of the HAT environment.)
        :param weapon_speed: (float) Speed of this weapon in meters per second.
        :param threat: (Threat) Target threat.
        :param weapon_type: (int) 0 or 1. What the intended type of this weapon will be.
        :param weapon_id: (str) A string ID for this specific weapon.
        :param rng: (np.random.RandomState) Numpy random number generator.
        """
        # defensive weapon, launched against a threat
        assert weapon_type == 0 or weapon_type == 1  # only two weapon types right now

        self.ship_id = ship_id
        self.ship_location = np.array(ship_location).astype(float)
        self.threat = threat
        self.weapon_type = weapon_type
        self.weapon_id = weapon_id
        launch_info = get_weapon_launch_info(
            self.threat.location, self.ship_location, self.threat.velocity, weapon_speed
        )
        self.timer = launch_info["time_to_intercept"]
        self.velocity = launch_info["weapon_velocity"]
        self.intercept_point = launch_info["intercept_point"]
        self.location = copy.deepcopy(self.ship_location)

        distance_to_threat = float(distance(ship_location, threat.location))

        # not currently using direction for pk, but could in the future
        # direction = self._compute_angle(self.ship_location, ship_orientation, threat.location)

        self.p_kill = get_pk(distance_to_threat, weapon_type, threat.threat_type)
        self.kill = True if rng.uniform(0.0, 1.0) < self.p_kill else False

    @staticmethod
    def _compute_angle(ship_location: np.ndarray, ship_orientation: float, threat_location: np.ndarray) -> float:
        """Get the angle to the threat from the ship."""
        diff = threat_location - ship_location
        angle = np.arctan2(diff[1], diff[0])
        degrees = np.rad2deg(angle) - ship_orientation
        if degrees < 0:
            degrees += 360
        return degrees

    def step(self) -> bool:
        self.timer -= 1
        assert self.timer > -1
        self.location += self.velocity
        if self.timer <= 0:
            return True
        else:
            return False

    def get_target_threat_id(self) -> str:
        return self.threat.threat_id

    def get_kill_success(self) -> bool:
        return self.kill

    def get_ship_id(self) -> int:
        return self.ship_id

    def get_weapon_id(self) -> str:
        return self.weapon_id

    def get_current_timer(self) -> float:
        return self.timer

    def get_p_kill(self) -> float:
        return self.p_kill
