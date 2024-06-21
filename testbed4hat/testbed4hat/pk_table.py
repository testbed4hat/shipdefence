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

def get_pk(distance: float, weapon_ind: int, threat_ind: int) -> float:
    """
    Hardcoded logic for computing probability of kill (PK) for weapons assigned to different threats, as a
    function of distance. Weapon 0 is more effective over long ranges, while weapon 1 is more
    effective over short ranges.
    :param distance: distance to threat [m]
    :param weapon_ind: 0 or 1 (currently only two weapon types)
    :param threat_ind: 0 or 1 (currently only two threat_types)
    :return: probability that defense will neutralize threat (assuming available and no other impacting factors)
    """
    if weapon_ind == 0:  # long range defense
        if threat_ind == 0:  # threat 0
            if distance < 1000:
                pk = 0.
            elif distance < 2000:
                pk = .9 * (distance-1000) / 1000
            elif distance < 25000:
                pk = 0.9
            elif distance < 32500:
                pk = 0.9 - .9 * (distance-25000) / 7500
            else:
                pk = 0.
        else:  # threat 1
            if distance < 1000:
                pk = 0.
            elif distance < 2000:
                pk = .7 * (distance - 1000) / 1000
            elif distance < 30000:
                pk = 0.7
            elif distance < 35000:
                pk = 0.7 - .7 * (distance - 30000) / 5000
            else:
                pk = 0.
    else:  # short range defense
        if threat_ind == 0:  # threat 0
            if distance < 1000:
                pk = 0.
            elif distance < 2000:
                pk = .95 * (distance - 1000) / 1000
            elif distance < 8000:
                pk = 0.95
            elif distance < 17500:
                pk = 0.95 - .95 * (distance - 8000) / 9500
            else:
                pk = 0.
        else:  # threat 1
            if distance < 1000:
                pk = 0.
            elif distance < 2000:
                pk = .85 * (distance - 1000) / 1000
            elif distance < 10000:
                pk = 0.85
            elif distance < 20000:
                pk = 0.85 - .85 * (distance - 10000) / 10000
            else:
                pk = 0.
    return pk


def get_pk_original(distance: float, direction: float, weapon_ind: int, threat_ind: int) -> float:
    """
    Hardcoded logic for computing probability of kill (PK) for weapons assigned to different threats, as a
    function of distance and direction.  Weapon 0 is more effective over long ranges, while weapon 1 is more
    effective over short ranges.  Currently, directionality is also included (both weapons are effective over
    3/4 of the sky; short-range favors left side of ship, long-range favors right side).
    :param distance: distance to threat [m]
    :param direction:  angle from heading of ship to threat (degrees)
    :param weapon_ind: 0 or 1 (currently only two weapon types)
    :param threat_ind: 0 or 1 (currently only two threat_types)
    :return: probability that defense will neutralize threat (assuming available and no other impacting factors)
    """
    direction = direction % 360
    if weapon_ind == 0:  # long range defense
        if 0 <= direction <= 135 or 225 <= direction:
            if threat_ind == 0:  # threat 0
                if distance < 1000:
                    pk = 0.
                elif distance < 2000:
                    pk = .9 * (distance-1000) / 1000
                elif distance < 25000:
                    pk = 0.9
                elif distance < 32500:
                    pk = 0.9 - .9 * (distance-25000) / 7500
                else:
                    pk = 0.
            else:  # threat 1
                if distance < 1000:
                    pk = 0.
                elif distance < 2000:
                    pk = .7 * (distance - 1000) / 1000
                elif distance < 30000:
                    pk = 0.7
                elif distance < 35000:
                    pk = 0.7 - .7 * (distance - 30000) / 5000
                else:
                    pk = 0.
        else:
            pk = 0.
    else:  # short range defense
        if 45 <= direction <= 315:
            if threat_ind == 0:  # threat 0
                if distance < 1000:
                    pk = 0.
                elif distance < 2000:
                    pk = .95 * (distance - 1000) / 1000
                elif distance < 8000:
                    pk = 0.95
                elif distance < 17500:
                    pk = 0.95 - .95 * (distance - 8000) / 9500
                else:
                    pk = 0.
            else:  # threat 1
                if distance < 1000:
                    pk = 0.
                elif distance < 2000:
                    pk = .85 * (distance - 1000) / 1000
                elif distance < 10000:
                    pk = 0.85
                elif distance < 20000:
                    pk = 0.85 - .85 * (distance - 10000) / 10000
                else:
                    pk = 0.
        else:
            pk = 0.
    return pk


def compute_notification_delay(distance: float, weapon_speed: float, threat_speed: float) -> float:
    """
    Very simple method for estimating delay until agent knows whether threat is neutralized.  Assumes everything
     is radial and constant velocity and that the agent is aware of an intercept or miss as soon as it occurs.
    :param distance: distance of threat when countermeasure is launched [m]
    :param weapon_speed: radial speed of blue defense [m/s]
    :param threat_speed: radial speed of red threat [m/s]
    :return: intercept time [s]
    """
    return distance / (weapon_speed + threat_speed)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    r = [item/1000 for item in range(0, 40000, 100)]
    a = [get_pk_original(d, 0, 0, 0) for d in range(0, 40000, 100)]
    b = [get_pk_original(d, 0, 0, 1) for d in range(0, 40000, 100)]
    c = [get_pk_original(d, 50, 1, 0) for d in range(0, 40000, 100)]
    d = [get_pk_original(d, 50, 1, 1) for d in range(0, 40000, 100)]
    plt.plot(r, a, linewidth=2)
    plt.plot(r, b, linewidth=2)
    plt.plot(r, c, linewidth=2)
    plt.plot(r, d, linewidth=2)
    plt.xlabel('Slant Range (km)', fontsize=12)
    plt.ylabel('PK', fontsize=12)
    plt.legend(['Weapon 1, Threat 1', 'Weapon 1, Threat 2', 'Weapon 2, Threat 1', 'Weapon 2, Threat 2'],
               loc='upper right')
    plt.title('PKs for Threat-Weapon Combinations', fontsize=14)
    plt.savefig('pk_table.png')