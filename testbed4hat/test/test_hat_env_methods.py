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

import unittest

from testbed4hat.hat_env import HatEnv
from testbed4hat.hat_env_config import HatEnvConfig
from testbed4hat.messages import WeaponLaunchInfo
from testbed4hat.ship import RELOADING, NO_INVENTORY
from testbed4hat.threat import Threat


class TestAddWeaponMethod(unittest.TestCase):
    def setUp(self):
        # Set up your environment class instance
        self.environment = HatEnv(HatEnvConfig({"render_env": False, "verbose": False}))
        self.environment.reset()  # Reset environment so ships are defined

        # Define mock threats
        self.mock_threat_1 = Threat((0, 0), 0, (1, 1), threat_id="threat_1_id")
        self.mock_threat_2 = Threat((0, 0), 0, (1, 1), threat_id="threat_2_id")

        # Set up mock threats and ships for testing
        self.environment.threats = {
            self.mock_threat_1.threat_id: self.mock_threat_1,
            self.mock_threat_2.threat_id: self.mock_threat_2,
            # Add more mock threats as needed
        }

    def test_add_weapon_successful(self):
        # Test adding a weapon successfully
        ship_id = 0
        threat_id = self.mock_threat_1.threat_id
        weapon_type = 1
        expected_weapon_id = "weapon_0"  # Assuming this is the expected weapon_id, first weapon added
        expected_launch_info = WeaponLaunchInfo(True, ship_id, threat_id, weapon_type, "BY_REQUEST",
                                                weapon_id=expected_weapon_id)

        launch_info = self.environment._add_weapon(ship_id, threat_id, weapon_type)

        expected_launch_info_dict = expected_launch_info.to_dict()
        launch_info_dict = launch_info.to_dict()
        for k, v in expected_launch_info_dict.items():
            self.assertEqual(launch_info_dict[k], v)
        self.assertIn(expected_weapon_id, [weapon.weapon_id for weapon in self.environment.weapons])

    def test_add_weapon_failure_inventory(self):
        # Test adding a weapon fails
        ship_id = 0
        threat_id = self.mock_threat_1.threat_id
        weapon_type = 1
        expected_failure_reason = NO_INVENTORY
        expected_launch_info = WeaponLaunchInfo(False, ship_id, threat_id, weapon_type, expected_failure_reason)

        self.environment.ship_1.num_weapon_1 = 0
        launch_info = self.environment._add_weapon(ship_id, threat_id, weapon_type)

        expected_launch_info_dict = expected_launch_info.to_dict()
        launch_info_dict = launch_info.to_dict()
        for k, v in expected_launch_info_dict.items():
            self.assertEqual(launch_info_dict[k], v)
        self.assertEqual(0, len(self.environment.weapons))  # Assert no weapon is added

    def test_add_weapon_failure_reloading(self):
        # Test adding a weapon fails
        ship_id = 0
        threat_id = self.mock_threat_1.threat_id
        weapon_type = 1
        expected_failure_reason = RELOADING
        expected_launch_info = WeaponLaunchInfo(False, ship_id, threat_id, weapon_type, expected_failure_reason)

        self.environment.ship_1.weapon_1_reloading = True
        launch_info = self.environment._add_weapon(ship_id, threat_id, weapon_type)

        expected_launch_info_dict = expected_launch_info.to_dict()
        launch_info_dict = launch_info.to_dict()
        for k, v in expected_launch_info_dict.items():
            self.assertEqual(launch_info_dict[k], v)
        self.assertEqual(0, len(self.environment.weapons))  # Assert no weapon is added


class TestAddThreatsMethod(unittest.TestCase):
    def setUp(self):
        self.environment = HatEnv(HatEnvConfig({"verbose": False, "render_env": False}))
        self.environment.reset()  # reset to make sure generator is defined
        self.threat_1_id = "threat_1"
        self.threat_2_id = "threat_2"

    def test_add_threats(self):
        # Set up test data
        s = 10  # Assuming a specific time in seconds
        threat1 = Threat((0, 0), 0, (1, 1), threat_id=self.threat_1_id)
        threat2 = Threat((0, 0), 0, (1, 1), threat_id=self.threat_2_id)

        # Mock the wave method of the threat generator to return the test threats
        def mock_wave(second):
            return [threat1, threat2]

        self.environment.generator.wave = mock_wave

        # Call the method under test
        self.environment._add_threats(s)

        # Check if threats are added correctly
        self.assertIn(self.threat_1_id, self.environment.threats)  # Check if threat with id 1 is added
        self.assertIn(self.threat_2_id, self.environment.threats)  # Check if threat with id 2 is added

        # Additional checks can be added based on your requirements


if __name__ == '__main__':
    unittest.main()
