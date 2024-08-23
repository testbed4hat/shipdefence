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

from typing import List, Union

import numpy as np

from .threat import Threat
from .utils import distance

DEFAULT_THREAT_0_SPEED = 10 * 1_000 / 60 / np.sqrt(2)  # 10 km/min -> m/s, from cartesian to radial
DEFAULT_THREAT_1_SPEED = 12 * 1_000 / 60 / np.sqrt(2)  # 12 km/min -> m/s, from cartesian to radial
DEGREE_IN_RADIANS = np.deg2rad(1)


class WaveGenerator:
    SCHEDULE_STRING_OPTIONS = ["random", "default"]

    def __init__(
        self,
        ship_0_location: tuple[float, float],
        ship_1_location: tuple[float, float],
        threat_0_kill_radius: float,
        threat_1_kill_radius: float,
        threat_0_speed: float = DEFAULT_THREAT_0_SPEED,
        threat_1_speed: float = DEFAULT_THREAT_1_SPEED,
        threat_0_kill_prob: float = 0.95,
        threat_1_kill_prob: float = 0.95,
        min_threat_distance: float = 50_000,
        max_threat_distance: float = 70_000,
        schedule: Union[str, dict] = "random",
        seed=None,
    ):
        """
        Object responsible for generating waves of threats for the HAT environment simulation. Waves are specified per
        second in the simulation. A max of one threat type per second allowed.
        :param ship_0_location: (float, float) Ship 1 location
        :param ship_1_location: (float, float) Ship 2 location
        :param threat_0_kill_radius: (float) How close threat 0 needs to be to kill a target ship
        :param threat_1_kill_radius: (float) How close threat 1 needs to be to kill a target ship
        :param threat_0_speed: (float) Speed of threat 0 in m/s
        :param threat_1_speed: (float) Speed of threat 1 in m/s
        :param threat_0_kill_prob: (float) Probability of killing a target ship for threat 0
        :param threat_1_kill_prob: (float) Probability of killing a target ship for threat 1
        :param min_threat_distance: (float) Minimum distance to spawn a threat m/s
        :param max_threat_distance: (float) Maximum distance to spawn a threat m/s
        :param schedule: (Union[str, dict]) How to schedule a threat. String options are 'random' (default) or
            'default'. "random" samples a schedule of 40 threats over a 15-minute period. 'default' has the following
            schedule:
                0: (1, 0),  # start of sim
                4 * 60: (1, 1),  # 4 minutes
                5 * 60 + 30: (0, 1),  # 5 minutes 30 seconds
                7 * 60: (1, 1)  # 7 minutes
            To specify a dictionary for the schedule, set keys as the second in time to generate the threat, and have a
            2-tuple as the value. Allowed values are (1, 0), (0, 1), and (1, 1). (1, 0) corresponds to launching a type
            0 threat at time t, (0, 1) corresponds to launching a type 1 threat at time t, and (1, 1) corresponds to
            launching one of each threat type at time t.
        :param seed: (int) Random seed
        """

        self.ship_0_location = ship_0_location
        self.ship_1_location = ship_1_location
        self.threat_0_kill_radius = threat_0_kill_radius
        self.threat_1_kill_radius = threat_1_kill_radius

        self.threat_0_speed = threat_0_speed
        self.threat_1_speed = threat_1_speed
        self.threat_0_kill_prob = threat_0_kill_prob
        self.threat_1_kill_prob = threat_1_kill_prob
        self.min_threat_distance = min_threat_distance
        self.max_threat_distance = max_threat_distance

        # schedule should be a mapping from second to (num_threat_0, num_threat_1)
        self.rng = np.random.default_rng(seed)
        if schedule == "default":
            self.schedule = {
                0: (1, 0),  # start of sim
                4 * 60: (1, 1),  # 4 minutes
                5 * 60 + 30: (0, 1),  # 5 minutes 30 seconds
                7 * 60: (1, 1),  # 7 minutes
            }
        elif schedule == "random":
            # up to 50 weapons spread over a schedule of between 10 and 20 minutes, only 1 of each weapon
            # can be launched per second
            min_threat_0 = 10
            max_threats = 50
            min_time_in_min = 5
            max_time_in_min = 10
            num_threat_0 = self.rng.integers(low=min_threat_0, high=max_threats)
            num_threat_1 = max_threats - num_threat_0

            episode_time = int(self.rng.integers(low=min_time_in_min, high=max_time_in_min))
            times1 = self.rng.choice(range(60 * episode_time), size=num_threat_0, replace=False)
            times2 = self.rng.choice(range(60 * episode_time), size=num_threat_1, replace=False)
            schedule = {}
            for t in range(60 * episode_time):
                if t in times1 and t in times2:
                    schedule[t] = (1, 1)
                elif t in times1:
                    schedule[t] = (1, 0)
                elif t in times2:
                    schedule[t] = (0, 1)
            self.schedule = schedule
        elif isinstance(schedule, dict):
            self.schedule = schedule
        else:
            raise ValueError("schedule must be either 'default', 'random', or a dict")

        # set the threat counter to keep track of threat IDs
        self.threat_counter: int = 1

    def _create_threat(self, threat_type):
        distance_sample = self.rng.uniform(self.min_threat_distance, self.max_threat_distance)  # distance from (0, 0)
        angle_sample = self.rng.uniform(0, 2 * np.pi)  # angle from (0, 0)
        position = np.cos(angle_sample) * distance_sample, np.sin(angle_sample) * distance_sample

        # pick a ship, and point the threat towards it
        ship_id = self.rng.choice([0, 1])
        ship_loc = self.ship_0_location if ship_id == 0 else self.ship_1_location
        threat_angle = np.arctan2(ship_loc[1] - position[1], ship_loc[0] - position[0])

        # if the threat gets too close to a closer threat when targeting the farther threat, switch targets
        other_ship_loc = self.ship_1_location if ship_id == 0 else self.ship_0_location
        other_ship_angle = np.arctan2(other_ship_loc[1] - position[1], other_ship_loc[0] - position[0])
        if abs(other_ship_angle - threat_angle) <= 3 * DEGREE_IN_RADIANS:
            if distance(other_ship_loc, position) < distance(ship_loc, position):
                threat_angle = other_ship_angle
                ship_id = 1 - ship_id

        if threat_type == 0:
            vel = self.threat_0_speed * np.cos(threat_angle), self.threat_0_speed * np.sin(threat_angle)
            kill_rad = self.threat_0_kill_radius
            kill_prob = self.threat_0_kill_prob
        elif threat_type == 1:
            vel = self.threat_1_speed * np.cos(threat_angle), self.threat_1_speed * np.sin(threat_angle)
            kill_rad = self.threat_1_kill_radius
            kill_prob = self.threat_1_kill_prob
        else:
            raise ValueError("Threat type must be either 0 or 1")

        threat_id = f"threat_{self.threat_counter}"
        self.threat_counter += 1
        threat = Threat(position, ship_id, vel, kill_rad, kill_prob, threat_type=threat_type, threat_id=threat_id)
        return threat

    def wave(self, second) -> List[Threat]:
        """
        Get a wave at time <second> if <second> is in the schedule.
        :param second: (int) The current time step in seconds.
        :return: (list) A list of Threat objects.
        """
        if second in self.schedule:
            threats = []
            num_threat_0, num_threat_1 = self.schedule[second]

            if num_threat_0 > 0:
                threats.append(self._create_threat(0))
            if num_threat_1 > 0:
                threats.append(self._create_threat(1))
            return threats
        return []
