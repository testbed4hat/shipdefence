from testbed4hat.testbed4hat.hat_env import HatEnv
from testbed4hat.testbed4hat.hat_env_config import HatEnvConfig
from typing import Union, Tuple


class SergeEnvRunner:

    def __init__(self):
        # todo:
        #  - Define how env should be initialized (do we get a config from Serge? or do we just listen for messages?)
        #  - Save run information to local storage

        self.env_config = HatEnvConfig()  # todo:  get config from init or from Serge
        self.env = None

    def _reset_env(self):
        obs, info = self.env.reset()
        terminated = False
        truncated = False
        step_counter = 0
        return obs, info, terminated, truncated, info, step_counter

    def _listen_for_message(self) -> Union[dict, None]:
        # todo: listen for messages. If message found, parse and return
        return None

    def _convert_wa_message_to_action(self, wa_message) -> list[Tuple[int, int, str]]:
        return []

    def _send_step_message(self, obs, reward, terminated, truncated, info, step_counter) -> None:
        # Convert the observation to a Serge message and send it to Serge
        return None

    def run(self):
        self.env = HatEnv(self.env_config)

        running = True
        reset = True
        step_counter = 0

        while running:
            if reset:
                obs, reward, terminated, truncated, info, step_counter = self._reset_env()
                reset = False

            msg = self._listen_for_message()

            if msg:
                if msg["templateId"] == "WA Message":  # Action message case (assign weapons to threats)
                    action = self._convert_wa_message_to_action(msg)
                    obs, reward, terminated, truncated, info = self.env.step(action)
                    self._send_obs_message(obs, reward, terminated, truncated, info, step_counter)

                elif msg["templateId"] == "Reset Message":  # Not a defined message yet, but a case for sim reset
                    reset = True

                elif msg["templateId"] == "Terminate Message":
                    running = False

                # todo: additional message types?
