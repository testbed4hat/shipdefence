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

import numpy as np

from .pk_table import get_pk


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> np.float64:
    return np.linalg.norm(np.array(p1) - np.array(p2))


def get_weapon_launch_info(threat_location: np.ndarray, ship_location: np.ndarray, threat_velocity: np.ndarray,
                           weapon_speed: float) -> Union[dict, None]:
    """Compute the weapon velocity, threat-intercept location, and time to intercept."""
    # Helpful: http://playtechs.blogspot.com/2007/04/aiming-at-moving-target.html

    target_pos = threat_location - ship_location  # compute from ship perspective, i.e. ship is at (0, 0)
    v_minus_speed = threat_velocity.dot(threat_velocity) - weapon_speed ** 2
    two_pos_times_vel = 2 * target_pos.dot(threat_velocity)
    pos_dot = np.dot(target_pos, target_pos)

    solutions = np.roots([v_minus_speed, two_pos_times_vel, pos_dot])
    solutions = [s for s in solutions if s > 0 and not np.iscomplex(s)]
    if len(solutions) == 0:
        return None
    time_to_intercept = np.min(solutions)

    intercept_point = threat_location + time_to_intercept * threat_velocity

    # get velocity vector
    intercept_angle = np.arctan2(intercept_point[1] - ship_location[1], intercept_point[0] - ship_location[0])
    weapon_vel = np.array([weapon_speed * np.cos(intercept_angle), weapon_speed * np.sin(intercept_angle)])

    assert np.all(np.isclose(ship_location + weapon_vel * time_to_intercept, intercept_point))

    return {"weapon_velocity": weapon_vel, "intercept_point": intercept_point,
            "time_to_intercept": time_to_intercept}


def compute_pk_ring_radii() -> Tuple[float, float, float]:
    r = [item for item in range(0, 40000, 100)]
    weapon_0_threat_0_pk = [get_pk(d, 0, 0) for d in range(0, 40000, 100)]
    weapon_0_threat_1_pk = [get_pk(d, 0, 1) for d in range(0, 40000, 100)]
    weapon_1_threat_0_pk = [get_pk(d, 1, 0) for d in range(0, 40000, 100)]
    weapon_1_threat_1_pk = [get_pk(d, 1, 1) for d in range(0, 40000, 100)]

    r_list = []
    for pk_list in [weapon_0_threat_0_pk, weapon_0_threat_1_pk, weapon_1_threat_0_pk, weapon_1_threat_1_pk]:
        a = np.array(pk_list)
        low = np.where(a <= 0.5)[0]
        i = np.where(np.diff(low) > 1)[0][0]
        low_idx = low[i]
        high_idx = low[i + 1]
        low_val = r[low_idx]
        high_val = r[high_idx]
        r_list.append((low_val, high_val))

    low_pk_ring_radius = float(np.mean([r[0] for r in r_list]))
    short_weapon_pk_radius = float(np.mean([r_list[2][1], r_list[3][1]]))  # weapon 1
    long_weapon_pk_radius = float(np.mean([r_list[0][1], r_list[1][1]]))  # weapon 0

    return low_pk_ring_radius, short_weapon_pk_radius, long_weapon_pk_radius



