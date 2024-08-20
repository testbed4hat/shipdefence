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

from .utils import distance


class Threat:

    def __init__(
        self,
        location: Tuple[float, float],
        target_ship_id: int,
        initial_velocity: Tuple[float, float],
        kill_radius: float = 500,
        kill_probability: float = 0.95,
        threat_type: int = 0,
        threat_id: str = "threat_0",
    ):
        # assume distance units are in meters, and velocity are in meters per second?
        assert threat_type in [0, 1]
        self.location = np.array(location)
        self.target_ship_id: int = target_ship_id
        self.velocity = np.array(initial_velocity)
        self.kill_radius: float = kill_radius
        self.kill_probability: float = kill_probability
        self.threat_type: int = threat_type
        self.threat_id: str = threat_id
        self.success: bool = np.random.uniform(low=0.0, high=1.0) < self.kill_probability

    def step(self):
        self.location += self.velocity

    def kill(self, ship_location):
        d = distance(ship_location, self.location)
        if d < self.kill_radius:
            return self.success
        return False
