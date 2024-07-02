from testbed4hat.testbed4hat.hat_env import HatEnv
from testbed4hat.testbed4hat.hat_env_config import HatEnvConfig
from typing import Union, Tuple
import requests
from serge import MSG_MAPPING_SHIPS, MSG_WA, MSG_CHAT, SergeGame

class SergeEnvRunner:
    WEAPON_STR_TO_INT = {"Long Range": 0, "Short Range": 1}

    def __init__(self, game_id: str, server_url: str = "https://serge-inet.herokuapp.com"):
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
        
        #serge setup vars
        self.game_id = game_id
        self.url = server_url
        self.serge_game = SergeGame(game_id=game_id, server_url=server_url)

        #serge state variables
        self.current_game_state: list[dict] | None = None
        self.wargame_last: list[dict] | None = None

        #bools
        self.should_get_wargame: bool = True
        self.should_get_wargame_last: bool = True
        self.should_send_message: bool = False
        self.should_send_chat_message: bool = False
        self.should_send_WA_message: bool = False
    
    def reset_function_list(self):
        self.function_list = list(self.function_map.keys())

    def set_current_game_state(self, data: list[dict] | None = None):
        if data != None:
            self.current_game_state = data
            return True
        else:
            #failed to update game state
            return False

    def set_wargame_last(self, data: list[dict] | None = None):
        if data != None:
            self.wargame_last = data
            return True
        else:
            #failed to update game state
            return False

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
        ship_number = 0 if wa_message['channel'] == self.serge_game_instance.MAPPING_SHIP[1] else 1  # todo: verify!
        weapon_type = self.WEAPON_STR_TO_INT[wa_message['message']["Weapon"]]  # todo: verify!
        threat_id = wa_message['message']["Title"]  # todo: verify!
        return ship_number, weapon_type, threat_id

    def _process_action_msg(self, message) -> None:
        action = self._convert_wa_message_to_action(message)

        '''
        We will action messages on a rolling basis, so just add it to the list of actions to send to the env, until 
        the turn is over.
        '''
        self.turn_actions.append(action)

    def _step_environment(self) -> None:
        self.obs, self.reward, self.terminated, self.truncated, self.info = self.env.step(self.turn_actions)
        self.turn += 1

    def _send_step_message(self) -> None:
        # Convert the observation to a Serge message and send it to Serge
        # Note: Not sure if this message type is defined yet on Serge side!
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

            if self.should_get_wargame:
               data = self.serge_game.get_wargame()
               self.set_current_game_state(data)

            if self.should_get_wargame_last:
                data = self.serge_game.get_wargame_last()
                self.set_wargame_last(data)
            
            if self.should_send_message:
                #self.serge_game.send_message({})
                pass

            if self.should_send_chat_message:
                #self.serge_game.send_chat_message("")
                pass

            if self.should_send_WA_message:
                #self.serge_game.send_WA_message()
                pass

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
