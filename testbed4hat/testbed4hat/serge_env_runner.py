from testbed4hat.testbed4hat.hat_env import HatEnv
from testbed4hat.testbed4hat.hat_env_config import HatEnvConfig
from typing import Union, Tuple


class SergeEnvRunner:
    WEAPON_STR_TO_INT = {"Long Range": 0, "Short Range": 1}

    def __init__(self):
        # todo:
        #  - Define how env should be initialized (do we get a config from Serge? or do we just listen for messages?)
        #  - Save run information to local storage

        self.env_config = HatEnvConfig()  # todo:  get config from init or from Serge
        self.env = None
        self.obs = None
        self.reward = None
        self.terminated = None
        self.truncated = None
        self.info = None
        self.turn = None
        self.turn_actions = None

    def _reset_env(self):
        self.obs, self.info = self.env.reset()
        self.terminated = False
        self.truncated = False
        self.turn = 0

    def _listen_for_message(self) -> Union[dict, None]:
        # todo: listen for messages. If message found, parse and return
        return None

    def _convert_wa_message_to_action(self, wa_message) -> Tuple[int, int, str]:
        # # WA message
        # msg_wa = {
        #   "_id": "2024-06-12T22:02:39.113Z",
        #   "messageType": "CustomMessage",
        #   "templateId": "WA Message",
        #   "details": {
        #     "channel": "lw50a2yz",
        #     "from": {
        #       "force": "Taskforce",
        #       "forceId": "f-taskforce",
        #       "forceColor": "#3dd0ff",
        #       "roleName": "AI Assistant",
        #       "roleId": {
        #         "forceId": "f-taskforce",
        #         "forceName": "Taskforce",
        #         "roleId": "ai-assistant",
        #         "roleName": "AI Assistant"
        #       },
        #       "iconURL": "http://localhost:8080/default_img/forceDefault.png"
        #     },
        #     "timestamp": "2024-06-12T22:02:39.113Z",
        #     "turnNumber": 0,
        #     "collaboration": {
        #       "status": "Pending review",
        #       "lastUpdated": "2024-06-12T22:02:39.113Z"
        #     }
        #   },
        #   "message": {
        #     "Threat": {
        #       "Detected type": "ASM",
        #       "Expected ETA": "15:09",
        #       "ID": "B01",
        #       "Ship Targeted": "Ship A",
        #       "Velocity": 850
        #     },
        #     "Title": "B01",
        #     "Weapon": "Long Range"
        #   }
        # }

        # Tuple is (ship_number: int, weapon_type: int, threat_id: str)
        ship_number = 0 if wa_message['channel'] == 'Ship 1' else 1  # todo: verify!
        weapon_type = self.WEAPON_STR_TO_INT[wa_message['message']["Weapon"]]  # todo: verify!
        threat_id = wa_message['message']["Title"]  # todo: verify!
        return ship_number, weapon_type, threat_id

    def _process_action_msg(self, message) -> None:
        action = self._convert_wa_message_to_action(message)

        '''
        Current mental model of actions is that we will action messages on a rolling basis, so just add it to the
        list of actions to send to the env, until the turn is over. This may be wrong.
        '''
        self.turn_actions.append(action)

    def _step_environment(self) -> None:
        self.obs, self.reward, self.terminated, self.truncated, self.info = self.env.step(self.turn_actions)
        self.turn += 1

    def _send_step_message(self) -> None:
        # Convert the observation to a Serge message and send it to Serge
        return None

    def run(self):
        self.env = HatEnv(self.env_config)

        running = True
        reset = True

        while running:
            if reset:
                self._reset_env()
                # todo: how to send reset information?
                #   E.g. ship locations?
                reset = False

            msg = self._listen_for_message()

            if msg:
                if msg["templateId"] == "WA Message":  # Action message case (assign weapons to threats)
                    self._process_action_msg(msg)

                elif msg["templateId"] == "End Turn Message":  # Not a defined message yet, but a case for end turn
                    self._step_environment()
                    self._send_step_message()

                elif msg["templateId"] == "Reset Message":  # Not a defined message yet, but a case for sim reset
                    reset = True

                elif msg["templateId"] == "Terminate Message":   # Not a defined message yet, but a case for end game
                    running = False

                # todo: additional message types?
