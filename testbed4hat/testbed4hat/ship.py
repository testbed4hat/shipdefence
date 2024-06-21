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

from typing import Tuple

import numpy as np

from .threat import Threat
from .weapon import Weapon

RELOADING = "RELOADING"
NO_INVENTORY = "NO INVENTORY"


class Ship:
    def __init__(self, location: Tuple[float, float],
                 orientation: float,
                 num_weapon_0: int,
                 num_weapon_1: int,
                 weapon_0_reload_time: int,
                 weapon_1_reload_time: int,
                 weapon_0_speed: float,
                 weapon_1_speed: float,
                 rng: np.random.RandomState,
                 ):
        """
        A Ship object used in the HAT simulation environment. Has a location and orientation, holds a number of
        weapons, and can launch weapons.
        :param location: (float, float) The location of the ship in meters.
        :param orientation: (float) The orientation of the ship in degrees.
        :param num_weapon_0: (int) Starting inventory count of weapon 0.
        :param num_weapon_1: (int) Starting inventory count of weapon 1.
        :param weapon_0_reload_time: (int) Number of seconds it takes to reload weapon 0.
        :param weapon_1_reload_time: (int) Number of seconds it takes to reload weapon 1.
        :param weapon_0_speed: (float) The speed at which weapon 0 travels in meters per second.
        :param weapon_1_speed: (float) The speed at which weapon 1 travels in meters per second.
        :param rng: Numpy random number generator.
        """
        self.location = location
        self.orientation = orientation
        self.num_weapon_0 = num_weapon_0
        self.num_weapon_1 = num_weapon_1
        self.weapon_0_reload_time = weapon_0_reload_time
        self.weapon_1_reload_time = weapon_1_reload_time
        self.alive = True
        self.death_clock = None
        self.weapon_0_reloading = False
        self.weapon_1_reloading = False

        self.weapon_0_reload_timer = 0
        self.weapon_1_reload_timer = False

        self.weapon_0_speed = weapon_0_speed
        self.weapon_1_speed = weapon_1_speed
        self.rng = rng

    def use_weapon_0(self, threat: Threat, weapon_id: str):
        if self.weapon_0_reloading:
            return RELOADING
        elif self.num_weapon_0 <= 0:
            return NO_INVENTORY
        else:
            self.num_weapon_0 -= 1
            self.weapon_0_reloading = True
            self.weapon_0_reload_timer = self.weapon_0_reload_time
            return Weapon(self.location, self.orientation, self.weapon_0_speed, threat, 0, weapon_id, self.rng)

    def use_weapon_1(self, threat: Threat, weapon_id: str):
        if self.weapon_1_reloading:
            return RELOADING
        elif self.num_weapon_1 <= 0:
            return NO_INVENTORY
        else:
            self.num_weapon_1 -= 1
            self.weapon_1_reloading = True
            self.weapon_1_reload_timer = self.weapon_1_reload_time
            return Weapon(self.location, self.orientation, self.weapon_1_speed, threat, 1, weapon_id, self.rng)

    def use_weapon(self, weapon_type: int, threat: Threat, weapon_id: str):
        if weapon_type == 0:
            return self.use_weapon_0(threat, weapon_id)
        elif weapon_type == 1:
            return self.use_weapon_1(threat, weapon_id)
        else:
            raise ValueError(f"Unknown weapon type: {weapon_type}, must be 0 or 1")

    def step(self):
        if self.weapon_0_reloading:
            self.weapon_0_reload_timer -= 1
            if self.weapon_0_reload_timer <= 0:
                self.weapon_0_reloading = False
        if self.weapon_1_reloading:
            self.weapon_1_reload_timer -= 1
            if self.weapon_1_reload_timer <= 0:
                self.weapon_1_reloading = False

    def weapon_inventory(self):
        return {"weapon_0_inventory": self.num_weapon_0, "weapon_1_inventory": self.num_weapon_1}
    
    def weapon_status(self):
        return {"weapon_0_reloading": self.weapon_0_reloading, "weapon_1_reloading": self.weapon_1_reloading}

    def make_dead(self, time: int):
        self.alive = False
        self.death_clock = time

    def is_dead(self) -> bool:
        return not self.alive

    def when_dead(self):
        return self.death_clock if self.death_clock is not None else None
