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

import warnings
from typing import Any, Union, Iterable, Tuple

import gymnasium as gym
import numpy as np
import pygame
from gymnasium.core import ObsType

from .messages import WeaponLaunchInfo, WeaponEndMessage, ShipDestroyedMessage, ThreatMissMessage
from .pk_table import get_pk
from .ship import Ship
from .threat import Threat
from .utils import distance, compute_pk_ring_radii
from .wave_generator import WaveGenerator
from .weapon import Weapon
from .hat_env_config import HatEnvConfig


class HatEnv(gym.Env):
    VALID_SHIP_IDS = {0, 1}

    def __init__(self, config: HatEnvConfig):
        self.config = config

        # set environment variables
        self.seed = self.config.seed
        self.seconds_per_timestep = self.config.seconds_per_timestep
        self.weapon_0_speed = self.config.weapon_0_speed
        self.weapon_1_speed = self.config.weapon_1_speed
        self.weapon_0_reload_time = self.config.weapon_0_reload_time
        self.weapon_1_reload_time = self.config.weapon_1_reload_time
        self.num_ship_0_weapon_0 = self.config.num_ship_0_weapon_0
        self.num_ship_0_weapon_1 = self.config.num_ship_0_weapon_1
        self.num_ship_1_weapon_0 = self.config.num_ship_1_weapon_0
        self.num_ship_1_weapon_1 = self.config.num_ship_1_weapon_1
        self.min_distance_between_ships = self.config.min_distance_between_ships
        self.max_distance_between_ships = self.config.max_distance_between_ships
        self.hard_ship_0_location = self.config.hard_ship_0_location
        self.hard_ship_1_location = self.config.hard_ship_1_location
        self.wasted_weapon_reward = self.config.wasted_weapon_reward
        self.target_hit_reward = self.config.target_hit_reward
        self.max_episode_time_in_seconds = self.config.max_episode_time_in_seconds
        self.verbose = self.config.verbose

        # The max number of each kind of weapon that can be launched per ship per turn. Used to warn users they are
        #   asking for too many weapon launches per turn, and to quite processing actions early, if needed.
        self.max_weapons_per_turn = {
            "weapon_0": self.seconds_per_timestep // self.weapon_0_reload_time,
            "weapon_1": self.seconds_per_timestep // self.weapon_1_reload_time,
        }
        # max actions per step are how many max weapons can be launched per turn for both boats. Used to warn users they
        #   are giving too many actions per turn, and to quite processing the actions list if it was too large
        self.max_actions_step = self.max_weapons_per_turn["weapon_0"] * 2 + self.max_weapons_per_turn["weapon_1"] * 2

        self.rng = np.random.RandomState(self.seed)

        # generator parameters
        self.threat_0_kill_radius = self.config.threat_0_kill_radius
        self.threat_1_kill_radius = self.config.threat_1_kill_radius
        self.threat_0_speed = self.config.threat_0_speed
        self.threat_1_speed = self.config.threat_1_speed
        self.threat_0_kill_prob = self.config.threat_0_kill_prob
        self.threat_1_kill_prob = self.config.threat_1_kill_prob
        self.min_threat_distance = self.config.min_threat_distance
        self.max_threat_distance = self.config.max_threat_distance
        self.schedule = self.config.schedule

        # render settings vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        self.render_env = self.config.render_env
        self.zoom = self.config.zoom
        self.screen_width = self.config.screen_width
        self.screen_height = self.config.screen_height

        #   amount to "shrink" plotting coordinates so that everything fits on the screen
        outside_of_screen = (self.max_threat_distance + 5000) * 2  # max threat distance plus 5km buffer, multiplied by
        # 2 because this is a radius, and the screen needs to extend both directions
        zoom_factor = self.config.zoom

        #   divide by smallest screen can be
        self.coordinate_size_reduction = outside_of_screen / min(self.screen_height, self.screen_width) / zoom_factor

        self.screen_background_color = (255, 255, 255)  # White
        self.font_color = self.config.font_color
        self.font_size = self.config.font_size
        self.display_threat_ids = self.config.display_threat_ids

        self.threat_0_size = self.config.threat_0_base_size / self.coordinate_size_reduction
        self.threat_1_size = self.config.threat_1_base_size / self.coordinate_size_reduction
        self.threat_0_color = self.config.threat_0_color
        self.threat_1_color = self.config.threat_1_color

        self.draw_threat_spawn_region = self.config.draw_threat_spawn_region

        self.weapon_0_size = self.config.weapon_0_base_size / self.coordinate_size_reduction
        self.weapon_1_size = self.config.weapon_1_base_size / self.coordinate_size_reduction
        self.weapon_0_color = self.config.weapon_0_color
        self.weapon_1_color = self.config.weapon_1_color

        self.ship_length = self.config.ship_base_length / self.coordinate_size_reduction
        self.ship_width = self.config.ship_base_width / self.coordinate_size_reduction
        self.ship_0_color = self.config.ship_0_color
        self.ship_1_color = self.config.ship_1_color

        self.low_pk_ring_radius, self.short_pk_ring_radius, self.long_pk_ring_radius = compute_pk_ring_radii()
        if self.verbose:
            print("Ring info:")
            print(f"\tLow PK Ring Radius: {self.low_pk_ring_radius} meters")
            print(f"\tShort PK Ring Radius: {self.short_pk_ring_radius} meters")
            print(f"\tLong PK Ring Radius: {self.long_pk_ring_radius} meters")
        self.low_pk_ring_color = (0, 255, 0)  # green
        self.short_pk_ring_color = self.weapon_1_color
        self.long_pk_ring_color = self.weapon_0_color

        if self.render_env:
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            if self.verbose:
                # Note: Convenience message, can be deleted if no longer useful
                print("Pixel info:")
                print(f"\t1 Pixel = {self.coordinate_size_reduction} meters")
        else:
            self.screen = None

        # render settings ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        # Instantiate variables to be set in <reset> method
        self.generator = None
        self.ship_0 = None
        self.ship_1 = None
        self.threats = None
        self.weapons: list[Weapon] = list()
        self.time_step = None
        self.time_seconds = None
        self.weapon_counter: int = 0
        self.threat_counter: int = 0
        self.action_queue = None
        self.step_messages = None

    def _warn(self, warning_text) -> None:
        """Convenience function for printing warning text only when verbose is True."""
        if self.verbose:
            warnings.warn(warning_text)

    def _get_ship(self, ship_id: int) -> Ship:
        assert ship_id in self.VALID_SHIP_IDS
        return self.ship_0 if ship_id == 0 else self.ship_1

    def _add_threats(self, second: int) -> None:
        """Get threats from the threat generator"""
        new_threats = self.generator.wave(second)
        for threat in new_threats:
            self.threats[threat.threat_id] = threat

    def _add_weapon(self, ship_id: int, threat_id: str, weapon_type: int) -> WeaponLaunchInfo:
        """Try to add a weapon to the environment from a ship, report result to the user."""
        assert isinstance(threat_id, str)
        assert isinstance(weapon_type, int)
        weapon_id = f"weapon_{self.weapon_counter}"
        threat = self.threats[threat_id]
        ship = self._get_ship(ship_id)
        weapon = ship.use_weapon(weapon_type, threat, weapon_id)
        if isinstance(weapon, Weapon):
            self.weapons.append(weapon)
            self.weapon_counter += 1
            return WeaponLaunchInfo(True, ship_id, threat_id, weapon_type, "BY_REQUEST",
                                    p_k=weapon.get_p_kill(), weapon_id=weapon_id)
        else:
            return WeaponLaunchInfo(False, ship_id, threat_id, weapon_type, weapon)

    def _queue_actions(self, action: Iterable[Tuple[int, int, str]]) -> None:
        """
        Put actions to be executed this step into a queue. Some number of actions may be executed at each second within
        the step.
        :param action: Iterable of actions of the form: (ship_id, weapon_type, "threat_id")
        """
        self.action_queue = []  # start with clean queue
        weapon_counter = {"ship_0": {"weapon_0": 0, "weapon_1": 0}, "ship_1": {"weapon_0": 0, "weapon_1": 0}}
        for ship_id, weapon_type, threat_id in action:
            assert ship_id in [0, 1]  # ship IDs are 0 and 1
            assert weapon_type in [0, 1]  # weapon types are 0 and 1
            assert isinstance(threat_id, str)  # threat IDS are strings
            ship_weapons_used = weapon_counter[f"ship_{ship_id}"][f"weapon_{weapon_type}"]
            max_ship_weapons_per_turn = self.max_weapons_per_turn[f"weapon_{weapon_type}"]
            if ship_weapons_used < max_ship_weapons_per_turn:
                weapon_counter[f"ship_{ship_id}"][f"weapon_{weapon_type}"] += 1
                self.action_queue.append((ship_id, weapon_type, threat_id))
            else:
                self._warn(f"Trying to fire too many of weapon {weapon_type} for ship {ship_id} in one turn")
                if len(self.action_queue) >= self.max_actions_step:
                    self._warn(f"Number of given actions exceeded max allowed per step. Max={self.max_actions_step}")
                    # quit because no more actions are allowed
                    break

    def _process_actions(self) -> list:
        """1 action per ship is processed per second. Weapon launches can fail, in which case, nothing happens."""
        actions_taken = []
        ships_act_available = [True, True]  # One for each ship
        if len(self.action_queue) > 0:
            new_action_queue = []
            for action in self.action_queue:
                ship_id, weapon_type, threat_id = action
                if ships_act_available[ship_id]:
                    if threat_id in self.threats:
                        weapon = self._add_weapon(ship_id, threat_id, weapon_type)
                        actions_taken.append(weapon)
                        if not weapon.launched and weapon.reason == "RELOADING":
                            new_action_queue.append(action)  # add the action back in so we can try again later
                    else:
                        self._warn(f"Tried to target a non-existing threat ID={threat_id}! Ignoring action")
                    ships_act_available[ship_id] = False
                else:
                    new_action_queue.append(action)

            self.action_queue = new_action_queue
        return actions_taken

    def _weapon_process(self, second) -> None:
        """Step each weapon, process outcomes, if any."""
        new_list = []
        for weapon in self.weapons:
            done = weapon.step()
            if done:
                if weapon.get_kill_success():
                    targeted_threat_id = weapon.get_target_threat_id()
                    destroyed_target = False
                    if targeted_threat_id in self.threats:
                        self.threats.pop(targeted_threat_id)
                        destroyed_target = True
                    message = WeaponEndMessage(weapon.get_weapon_id(), targeted_threat_id, second, destroyed_target)
                    self.step_messages.append(message)
            elif weapon.get_target_threat_id() not in self.threats:
                message = WeaponEndMessage(weapon.get_weapon_id(), weapon.get_target_threat_id(), second, False)
                self.step_messages.append(message)
            else:
                new_list.append(weapon)
        self.weapons = new_list

    def _threat_process(self, second) -> None:
        """Get new threats from generator, then update each threat by 1 second."""
        # Note: We use this to remove threats at the end, because removing a key from a dict mid-iteration makes Python
        #   mad. This method of removing threats should not affect the simulation at all, since this is logic for a
        #   'miss'.
        threats_to_pop = []
        for threat_id, threat in self.threats.items():
            threat.step()
            ship = self._get_ship(threat.target_ship_id)
            d = float(distance(ship.location, threat.location))
            if threat.kill(ship.location):
                ship.make_dead(second)
                message = ShipDestroyedMessage(threat.target_ship_id, threat_id, second, d)
                self.step_messages.append(message)
                break
            elif d < 100:
                threats_to_pop.append(threat_id)
                message = ThreatMissMessage(threat_id, threat.target_ship_id, second)
                self.step_messages.append(message)

        # remove any threats that were eliminated in this step
        if len(threats_to_pop) > 0:
            for threat_id in threats_to_pop:
                self.threats.pop(threat_id)

    def _threat_observation(self, ship_id: int, threat: Threat) -> dict:
        ship = self._get_ship(ship_id)
        threat_dist = float(distance(ship.location, threat.location))
        threat_abs_angle = np.arctan2(threat.location[1] - ship.location[1], threat.location[0] - ship.location[0])
        threat_angle = ship.orientation - np.rad2deg(threat_abs_angle)

        weapon_0_p_kill = get_pk(threat_dist, 0, threat.threat_type)  # threat angle not used for pk now
        weapon_1_p_kill = get_pk(threat_dist, 1, threat.threat_type)

        weapons_assigned = [w.weapon_id for w in self.weapons if w.threat.threat_id == threat.threat_id]
        weapons_assigned_type = [w.weapon_type for w in self.weapons if w.threat.threat_id == threat.threat_id]
        weapons_assigned_p_kill = [w.p_kill for w in self.weapons if w.threat.threat_id == threat.threat_id]

        target_ship = self._get_ship(threat.target_ship_id)
        target_location = target_ship.location
        target_dist = distance(target_location, threat.location)
        estimated_time_to_arrival = target_dist / np.linalg.norm(threat.velocity)

        obs = {
            "threat_id": threat.threat_id,
            "threat_type": threat.threat_type,
            "distance": threat_dist,
            "angle": threat_angle,
            "location": threat.location,
            "velocity": threat.velocity,
            "weapon_0_kill_probability": weapon_0_p_kill,
            "weapon_1_kill_probability": weapon_1_p_kill,
            "weapons_assigned": weapons_assigned,
            "weapons_assigned_type": weapons_assigned_type,
            "weapons_assigned_p_kill": weapons_assigned_p_kill,
            "estimated_time_of_arrival": estimated_time_to_arrival,
            "target_ship": threat.target_ship_id,
        }

        return obs

    def _weapon_observation(self, ship_id: int, weapon: Weapon) -> dict:
        ship = self._get_ship(ship_id)
        weapon_dist = distance(ship.location, weapon.location)
        weapon_abs_angle = np.arctan2(weapon.location[1] - ship.location[1], weapon.location[0] - ship.location[0])
        weapon_angle = ship.orientation - np.rad2deg(weapon_abs_angle)
        obs = {
            "weapon_id": weapon.weapon_id,
            "weapon_type": weapon.weapon_type,
            "target_id": weapon.get_target_threat_id(),
            "ship_id": weapon.get_ship_id(),
            "time_left": weapon.get_current_timer(),
            "probability_of_kill": weapon.get_p_kill(),
            "distance": weapon_dist,
            "angle": weapon_angle,
            "location": weapon.location,
        }
        return obs

    def _make_observation(
        self, launches: list[WeaponLaunchInfo], failures: dict[tuple[int, str, int], WeaponLaunchInfo]
    ) -> dict:
        ship_0_obs = {
            "location": self.ship_0.location,
            "threats": [self._threat_observation(0, threat) for threat_id, threat in self.threats.items()],
            "weapons": [self._weapon_observation(0, weapon) for weapon in self.weapons],
            "inventory": self.ship_0.weapon_inventory()
        }

        # get ship 2 observation
        ship_1_obs = {
            "location": self.ship_1.location,
            "threats": [self._threat_observation(1, threat) for threat_id, threat in self.threats.items()],
            "weapons": [self._weapon_observation(1, weapon) for weapon in self.weapons],
            "inventory": self.ship_1.weapon_inventory()
        }        # Aggregate action (weapon) information
        launched = [l_info.to_obs() for l_info in launches]
        failed = [l_info.to_obs() for l_info in failures.values()]

        # Add any additional messages collected during the step
        messages = [m.to_string() for m in self.step_messages]
        return {
            "ship_0": ship_0_obs,
            "ship_1": ship_1_obs,
            "launched": launched,
            "failed": failed,
            "messages": messages,
        }

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:

        if seed is not None:
            self.seed = seed
            self.rng = np.random.RandomState(seed)

        self.time_step = 0
        self.time_seconds = 0

        if self.hard_ship_0_location is None:
            ship_0_angle = np.random.uniform(0, 2 * np.pi)
            ship_0_radius = np.random.uniform(0, self.max_distance_between_ships)
            ship_0_loc = (ship_0_radius * np.cos(ship_0_angle), ship_0_radius * np.sin(ship_0_angle))
        else:
            ship_0_loc = self.hard_ship_0_location

        if self.hard_ship_1_location is None:
            ship_1_angle = np.random.uniform(0, 2 * np.pi)
            ship_1_radius = np.random.uniform(0, self.max_distance_between_ships)
            ship_1_loc = (ship_1_radius * np.cos(ship_1_angle), ship_1_radius * np.sin(ship_1_angle))
        else:
            ship_1_loc = self.hard_ship_1_location

        # update the ships' locations to get a minimum distance, as long as both locations are not prescribed
        if self.hard_ship_0_location is None or self.hard_ship_1_location is None:
            while not (
                self.min_distance_between_ships <= distance(ship_0_loc, ship_1_loc) <= self.max_distance_between_ships
            ):
                if self.hard_ship_1_location is not None:
                    ship_0_angle = np.random.uniform(0, 2 * np.pi)
                    ship_0_radius = np.random.uniform(0, self.max_distance_between_ships)
                    ship_0_loc = (ship_0_radius * np.cos(ship_0_angle), ship_0_radius * np.sin(ship_0_angle))
                else:
                    ship_1_angle = np.random.uniform(0, 2 * np.pi)
                    ship_1_radius = np.random.uniform(0, self.max_distance_between_ships)
                    ship_1_loc = (ship_1_radius * np.cos(ship_1_angle), ship_1_radius * np.sin(ship_1_angle))

        ship_0_orientation = np.rad2deg(np.random.uniform(0, 2 * np.pi))
        ship_1_orientation = np.rad2deg(np.random.uniform(0, 2 * np.pi))

        self.ship_0 = Ship(
            0,
            ship_0_loc,
            ship_0_orientation,
            self.num_ship_0_weapon_0,
            self.num_ship_0_weapon_1,
            self.weapon_0_reload_time,
            self.weapon_1_reload_time,
            self.weapon_0_speed,
            self.weapon_1_speed,
            self.rng,
        )
        self.ship_1 = Ship(
            1,
            ship_1_loc,
            ship_1_orientation,
            self.num_ship_1_weapon_0,
            self.num_ship_1_weapon_1,
            self.weapon_0_reload_time,
            self.weapon_1_reload_time,
            self.weapon_0_speed,
            self.weapon_1_speed,
            self.rng,
        )

        if self.verbose:
            # Note: Convenience message, can be deleted if no longer useful
            print("Ship location info:")
            print(f"\tShip 1 location: {ship_0_loc}, \n\tShip 2 location: {ship_1_loc}")

        self.generator = WaveGenerator(
            ship_0_loc,
            ship_1_loc,
            self.threat_0_kill_radius,
            self.threat_1_kill_radius,
            threat_0_speed=self.threat_0_speed,
            threat_1_speed=self.threat_1_speed,
            threat_0_kill_prob=self.threat_0_kill_prob,
            threat_1_kill_prob=self.threat_1_kill_prob,
            min_threat_distance=self.min_threat_distance,
            max_threat_distance=self.max_threat_distance,
            schedule=self.schedule,
            seed=self.rng.randint(0, 99999),
        )

        self.threats = {}
        self.weapons = []
        self.action_queue = []
        self.step_messages = []

        self.weapon_counter = 0

        if self.render_env:
            if self.screen is not None:
                self.screen.fill(self.screen_background_color)

        return self._make_observation([], {}), {}

    def _reward_terminated_truncated(self, messages: list, launches: list) -> tuple[Union[int, float], bool, bool]:
        """Create reward, terminated, and truncated values for a step."""
        # if a ship dies, game over, reward = -5
        if self.ship_0.is_dead() or self.ship_1.is_dead():
            reward = -5
            terminated = True
            truncated = False
        else:
            # Episode ends after max time in seconds
            truncated = self.time_seconds >= self.max_episode_time_in_seconds
            terminated = False

            # reward is 5 for getting to the end without dying, 0 otherwise; minus some for wasting weapons
            reward = 5 if truncated else 0

            # Get wasted weapon rewards this step
            for m in messages:
                if isinstance(m, WeaponEndMessage):
                    if m.destroyed_target:
                        # Reward for hitting a target
                        reward += self.target_hit_reward
                    else:
                        reward += self.wasted_weapon_reward

            for weapon in launches:
                # Reward mapping from p_kill to reward in [-1, 1]
                # scale weapon p_k to [-1, 1]
                reward += 2 * weapon.p_k - 1

        return reward, terminated, truncated

    def step(self, action: list[tuple[int, int, str]]) -> ObsType:
        self._queue_actions(action)

        # process current weapon steps and threat steps in seconds
        user_info_launches = []
        user_info_failures = {}
        self.step_messages = []
        for sec in range(self.seconds_per_timestep):

            # break if game over
            if self.ship_0.is_dead() or self.ship_1.is_dead():
                break

            # process given actions
            actions_taken = self._process_actions()

            # Compile successful and failed weapon launches to send to user
            for action in actions_taken:
                if action.launched:
                    user_info_launches.append(action)
                    key = action.make_key()
                    if key in user_info_failures.keys():
                        # Failed launch eventually succeeded, so remove from failures
                        del user_info_failures[key]
                else:
                    key = action.make_key()
                    user_info_failures[key] = action

            # Process weapon behaviors
            self._weapon_process(self.time_seconds)
            # Get new threats from generator
            self._add_threats(self.time_seconds)
            # Process threat behaviors
            self._threat_process(self.time_seconds)

            # Step the ships
            self.ship_0.step()
            self.ship_1.step()

            # Render if configured
            if self.render_env:
                self.render()

            self.time_seconds += 1

        reward, terminated, truncated = self._reward_terminated_truncated(self.step_messages, user_info_launches)
        info = {}
        return self._make_observation(user_info_launches, user_info_failures), reward, terminated, truncated, info

    def _draw_rotated_and_rounded_rect(self, screen, color, x, y, ship_length, ship_width, angle) -> None:
        """Draw a ship-looking shape"""
        # Thank you, ChatGPT
        # Create a surface to draw the rectangle on
        rect_surface = pygame.Surface((ship_length, ship_width), pygame.SRCALPHA)
        rect_surface.fill(self.screen_background_color)

        # Draw the rounded end
        pygame.draw.rect(rect_surface, color, (0, 0, ship_length - ship_width / 2, ship_width))
        pygame.draw.circle(rect_surface, color, (ship_length - ship_width // 2, ship_width // 2), ship_width // 2)

        # Rotate the rectangle
        rotated_surface = pygame.transform.rotate(rect_surface, angle)
        rotated_rect = rotated_surface.get_rect(center=(x, y))

        # Draw the rotated rectangle onto the screen
        screen.blit(rotated_surface, rotated_rect)

    def _draw_threat(self, threat: Threat) -> None:
        color = self.threat_0_color if threat.threat_type == 0 else self.threat_1_color
        size = self.threat_0_size if threat.threat_type == 0 else self.threat_1_size
        x, y = threat.location
        # bring everything closer since the screen is not as big as the world
        x /= self.coordinate_size_reduction
        y /= self.coordinate_size_reduction
        # translate to screen coords
        x += self.screen_width // 2
        y += self.screen_height // 2
        pygame.draw.circle(self.screen, color, (x, y), size)

        if self.display_threat_ids:
            font = pygame.font.Font(None, self.font_size)
            text = font.render(threat.threat_id, True, self.font_color)
            text = pygame.transform.flip(text, False, True)
            self.screen.blit(text, (x, y))

    def _draw_weapon(self, weapon: Weapon) -> None:
        color = self.weapon_0_color if weapon.weapon_type == 0 else self.weapon_1_color
        size = self.weapon_0_size if weapon.weapon_type == 0 else self.weapon_1_size
        x, y = weapon.location
        # bring everything closer since the screen is not as big as the world
        x /= self.coordinate_size_reduction
        y /= self.coordinate_size_reduction
        # translate to screen coords
        x += self.screen_width // 2
        y += self.screen_height // 2
        pygame.draw.circle(self.screen, color, (x, y), size)

    def _draw_ship(self, ship: Ship) -> None:
        color = self.ship_0_color if ship is self.ship_0 else self.ship_1_color
        ship_length = self.ship_length
        ship_width = self.ship_width
        x = ship.location[0] - ship_width // 2
        y = ship.location[1] - ship_length // 2

        # bring everything closer since the screen is not as big as the world
        x /= self.coordinate_size_reduction
        y /= self.coordinate_size_reduction
        # translate to screen coords
        x += self.screen_width // 2
        y += self.screen_height // 2
        self._draw_rotated_and_rounded_rect(self.screen, color, x, y, ship_length, ship_width, ship.orientation)
        # pygame.draw.rect(self.screen, color, pygame.Rect(x, y, width, height))

        # draw the kill radius around the ship
        x = (ship.location[0] / self.coordinate_size_reduction) + self.screen_width // 2
        y = (ship.location[1] / self.coordinate_size_reduction) + self.screen_height // 2

        t0_kr = self.threat_0_kill_radius / self.coordinate_size_reduction
        t1_kr = self.threat_1_kill_radius / self.coordinate_size_reduction

        # draw circles show how close a threat needs to be to kill the ship
        pygame.draw.circle(self.screen, self.threat_0_color, (x, y), t0_kr, width=1)
        pygame.draw.circle(self.screen, self.threat_1_color, (x, y), t1_kr, width=1)

    def _draw_crosshair(self, screen, color, size) -> None:
        """Put a crosshair on the screen at the (0, 0) point as a reference for the user"""
        # Thank you, ChatGPT
        width, height = self.screen_width, self.screen_height
        size = size / self.coordinate_size_reduction
        # Draw horizontal line
        pygame.draw.line(screen, color, (width // 2 - size // 2, height // 2), (width // 2 + size // 2, height // 2))
        # Draw vertical line
        pygame.draw.line(screen, color, (width // 2, height // 2 - size // 2), (width // 2, height // 2 + size // 2))

    def _draw_weapon_rings(self) -> None:
        # draw the inner effective radius (small, so one for each ship)
        x = (self.ship_0.location[0] / self.coordinate_size_reduction) + self.screen_width // 2
        y = (self.ship_0.location[1] / self.coordinate_size_reduction) + self.screen_height // 2
        r = self.low_pk_ring_radius / self.coordinate_size_reduction
        pygame.draw.circle(self.screen, self.low_pk_ring_color, (x, y), r, width=1)

        x = (self.ship_1.location[0] / self.coordinate_size_reduction) + self.screen_width // 2
        y = (self.ship_1.location[1] / self.coordinate_size_reduction) + self.screen_height // 2
        r = self.low_pk_ring_radius / self.coordinate_size_reduction
        pygame.draw.circle(self.screen, self.low_pk_ring_color, (x, y), r, width=1)

        # draw outer effective range rings for each weapon, centered at the mean position of the two ships
        x = np.mean([self.ship_0.location[0], self.ship_1.location[0]])
        y = np.mean([self.ship_0.location[1], self.ship_1.location[1]])

        # bring everything closer since the screen is not as big as the world
        x /= self.coordinate_size_reduction
        y /= self.coordinate_size_reduction
        # translate to screen coords
        x += self.screen_width // 2
        y += self.screen_height // 2
        center = (float(x), float(y))

        # short weapon (1) outer ring
        r = self.short_pk_ring_radius / self.coordinate_size_reduction
        pygame.draw.circle(self.screen, self.short_pk_ring_color, center, r, width=1)

        # long weapon (0) outer ring
        r = self.long_pk_ring_radius / self.coordinate_size_reduction
        pygame.draw.circle(self.screen, self.long_pk_ring_color, center, r, width=1)

    def _draw_threat_spawn_region(self) -> None:
        # Draw a transparent reddish region where the threats are allowed to spawn
        x, y = 0, 0
        x += self.screen_width // 2
        y += self.screen_height // 2

        r = self.max_threat_distance / self.coordinate_size_reduction
        w = r - self.min_threat_distance / self.coordinate_size_reduction

        c_surface = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
        c_surface.set_colorkey((215, 215, 215))
        c_surface.set_alpha(25)
        pygame.draw.circle(c_surface, (255, 0, 0), (r, r), r, width=int(w))
        self.screen.blit(c_surface, (x - r, y - r))

    def render(self) -> None:
        self.screen.fill(self.screen_background_color)
        self._draw_crosshair(self.screen, (0, 0, 0), 500)
        for threat in self.threats.values():
            self._draw_threat(threat)
        for weapon in self.weapons:
            self._draw_weapon(weapon)
        self._draw_ship(self.ship_0)
        self._draw_ship(self.ship_1)
        self._draw_weapon_rings()
        if self.draw_threat_spawn_region:
            self._draw_threat_spawn_region()
        self.screen.blit(pygame.transform.flip(self.screen, False, True), (0, 0))
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    def __del__(self):
        pygame.quit()
