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
from testbed4hat.testbed4hat.weapon import Weapon


class WeaponLaunchInfo:
    def __init__(
        self,
        launched: bool,
        ship_id: int,
        threat_id: str,
        weapon_type: int,
        reason: str,
        p_k: float = None,
        weapon_id: str = None,
    ):
        assert isinstance(launched, bool)
        assert isinstance(ship_id, int)
        assert isinstance(threat_id, str)
        assert isinstance(weapon_type, int)
        assert isinstance(reason, str)
        assert isinstance(p_k, float) or p_k is None
        if weapon_id is not None:
            assert isinstance(weapon_id, str)
        self.launched = launched
        self.ship_id = ship_id
        self.threat_id = threat_id
        self.weapon_type = weapon_type
        self.reason = reason
        self.p_k = p_k
        self.weapon_id = weapon_id

    def to_dict(self):
        return self.__dict__.copy()

    def to_obs(self):
        d = self.to_dict()
        success = d.pop("launched")
        if success:
            return d
        else:
            d.pop("weapon_id")
            return d

    def to_string(self):
        text = ""
        for k, v in self.to_dict().items():
            text += f"{k}: {v}\n"
        return text

    def make_key(self):
        return self.ship_id, self.threat_id, self.weapon_type


class ShipDestroyedMessage:
    def __init__(self, ship_id: int, threat_id: str, second: int, distance: float):
        self.ship_id = ship_id
        self.threat_id = threat_id
        self.second = second
        self.distance = distance

    def to_dict(self):
        return self.__dict__.copy()

    def to_string(self):
        return f"Ship {self.ship_id} killed by {self.threat_id} at time {self.second} at distance " f"{self.distance}."


class WeaponEndMessage:
    def __init__(self, weapon: dict, second: int, destroyed_target: bool):
        self.weapon: dict = weapon
        self.second: int = second
        self.destroyed_target: bool = destroyed_target

    def to_dict(self):
        return self.__dict__.copy()

    def to_string(self):
        if self.destroyed_target:
            return f"Weapon {self.weapon['weapon_id']} destroyed target {self.weapon['target_id']} at time s={self.second}."
        else:
            return f"Weapon {self.weapon['weapon_id']} targeting {self.weapon['target_id']} was wasted, target already destroyed"


class ThreatMissMessage:
    def __init__(self, threat_obs: dict, second: int):
        self.threat_obs: dict = threat_obs
        self.second = second

    def to_dict(self):
        return self.__dict__.copy()

    def to_string(self):
        return f"Threat {self.threat_obs['threat_id']} missed target ship {self.threat_obs['target_ship']} at time s={self.second}."
