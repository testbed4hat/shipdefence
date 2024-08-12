__package__ = "testbed4hat.provenance"

from collections import defaultdict, namedtuple
import csv
from datetime import datetime
import json
import logging
from pathlib import Path
from typing import Iterable, Optional

from munch import munchify

from ..testbed4hat.serge import SergeGame


logger = logging.getLogger(__name__)

MessageSendingBinding = namedtuple(
    "MessageSendingBinding",
    [
        "isA",
        "sender",
        "message",
        "message_type",
        "cserial",
        "channel0",
        "channel1",
        "channel_type",
        "message_content",
    ],
)
MessageReadingBinding = namedtuple(
    "MessageReadingBinding",
    [
        "isA",
        "rserial",
        "role0",
        "role1",
        "role_type",
        "fserial",
        "force0",
        "force1",
        "force_name",
        "name",
        "message",
        "channel",
    ],
)
PlanSubmittingBinding = namedtuple(
    "PlanSubmittingBinding",
    [
        "isA",
        "sender",
        "aserial",
        "asset",
        "force",
        "plan",
        "plan_type",
        "planning_turn",
        "turn_number",
        "plan_content",
        "previous_plan",
    ],
)
EndturnActivityBinding = namedtuple(
    "EndturnActivityBinding",
    [
        "isA",
        "act",
        "act_type",
        "role",
        "plan",
        "aserial",
        "asset0",
        "asset1",
        "asset_type",
        "fserial",
        "force0",
        "force1",
        "name",
        "turn_number",
        "condition",
        "state",
        "speed",
        "position",
        "startTime",
        "endTime",
    ],
)
EndturnUpdateBinding = namedtuple(
    "EndturnUpdateBinding",
    [
        "isA",
        "message",
        "plan",
        "aserial",
        "asset0",
        "asset1",
        "asset_type",
        "fserial",
        "force0",
        "force1",
        "name",
        "condition",
        "state",
        "speed",
        "position",
    ],
)
PerceptionUpdateBinding = namedtuple(
    "PerceptionUpdateBinding",
    [
        "isA",
        "rserial",
        "role0",
        "role1",
        "role_type",
        "fserial",
        "force0",
        "force1",
        "force_name",
        "name",
        "asset",
    ],
)
RoleBinding = namedtuple(
    "RoleBinding",
    ["isA", "rserial", "role", "role_type", "fserial", "force", "force_name", "name"],
)
AssetBinding = namedtuple(
    "AssetBinding",
    [
        "isA",
        "aserial",
        "asset",
        "asset_type",
        "fserial",
        "force",
        "force_name",
        "name",
        "contact_id",
        "position",
    ],
)
ForceBinding = namedtuple(
    "ForceBinding",
    ["isA", "fserial", "force", "name"],
)
ChannelBinding = namedtuple(
    "ChannelBinding",
    ["isA", "cserial", "channel", "channel_type", "name"],
)


def ensure_valid_localname(value: str) -> str:
    return value.replace(" ", "").replace("(", ".").replace(")", "")


def convert_to_type(value: str) -> str:
    return ensure_valid_localname(value.title())


class MutableGameObject:
    def __init__(self, serial: str):
        self.serial = serial
        self.version: int = 0
        self.previous_version = None

    def create_new_version(self, new_version: int | float = None):
        self.previous_version = self.version
        self.version = new_version if new_version is not None else self.version + 1

    @property
    def curr_version_id(self):
        return f"{self.serial}/{self.version}"

    @property
    def prev_version_id(self):
        return f"{self.serial}/{self.previous_version}" if self.previous_version is not None else None


class Role(MutableGameObject):
    def __init__(self, game: "ShipDefenceWorld", role_id, role_type, name, force):
        super().__init__(role_id)
        self.game = game
        self.role_type: str = role_type
        self.name: str = name
        self.force: Force = force

    @property
    def bindings(self) -> RoleBinding:
        return RoleBinding(
            "role",
            self.serial,
            self.curr_version_id,
            self.role_type,
            self.force.serial,  # fserial
            self.force.curr_version_id,  # force
            self.force.name,  # force_name
            self.name,
        )

    def read_message(self, message_id: float, channel_id: str):
        self.create_new_version()
        self.force.create_new_version()
        self.game.record_bindings(
            MessageReadingBinding(
                "message_reading",
                self.serial,  # rserial
                self.prev_version_id,  # role0
                self.curr_version_id,  # role1
                self.role_type,  # role_type
                self.force.serial,  # fserial
                self.force.prev_version_id,  # force0
                self.force.curr_version_id,  # force1
                self.force.name,  # force_name
                self.name,  # name
                message_id,  # message
                channel_id,  # channel
            )
        )


class Asset(MutableGameObject):
    def __init__(self, asset_id, contact_id, name, platform_type, force, position):
        super().__init__(asset_id)
        self.contact_id: str = contact_id
        self.name: str = name
        self.platform_type: str = platform_type
        self.force: Force = force
        self.condition: str | None = None
        self.position: str = position
        self.state = None
        self.speed = None

    @property
    def bindings(self) -> AssetBinding:
        return AssetBinding(
            "asset",
            self.serial,  # aserial
            self.curr_version_id,  # asset
            self.platform_type,
            self.force.serial,  # fserial
            self.force.curr_version_id,  # force
            self.force.name,  # force_name
            self.name,
            self.contact_id,
            self.position,
        )

    def update_state(self, condition, position, state, speed):
        self.create_new_version()
        self.condition = condition
        self.position = position
        self.state = state
        self.speed = speed


class Force(MutableGameObject):
    def __init__(self, force_id, name):
        super().__init__(force_id)
        self.name: str = name
        self.roles: dict[str, Role] = dict()
        self.assets: dict[str, Asset] = dict()
        self.perceptions: set[Asset] = set()

    def add_role(self, role: Role):
        self.roles[role.serial] = role

    def get_the_first_role(self) -> Role | None:
        # FIXME: a force may have more than one role!
        for role in self.roles.values():
            return role
        return None

    def add_asset(self, asset: Asset):
        self.assets[asset.serial] = asset

    def reset_perceptions(self):
        self.perceptions = set()

    def add_perception(self, asset):
        if asset.serial not in self.assets:
            # only adding perception of other forces' assets
            self.perceptions.add(asset)

    def perception_update_bindings(self):
        # returns all perception_update bindings when a new turn is started
        return [
            PerceptionUpdateBinding(
                "perception_update",
                role.serial,  # rserial
                role.prev_version_id,  # role0
                role.curr_version_id,  # role1
                role.role_type,  # role_type
                self.serial,  # fserial
                self.prev_version_id,  # force0
                self.curr_version_id,  # force1
                self.name,  # force_name
                role.name,  # name
                asset.curr_version_id,  # asset
            )
            for role in self.roles.values()
            for asset in self.perceptions
        ]

    @property
    def bindings(self) -> ForceBinding:
        return ForceBinding(
            "force",
            self.serial,
            self.curr_version_id,
            self.name,
        )


class Channel(MutableGameObject):
    def __init__(
        self,
        game: "ShipDefenceWorld",
        channel_id: str,
        channel_type: str,
        name: str,
        participants: Iterable[Role],
    ):
        super().__init__(channel_id)
        self.game = game
        self.channel_type = channel_type
        self.name = name
        self.participants: Iterable[Role] = participants

    @property
    def bindings(self) -> ChannelBinding:
        return ChannelBinding(
            "channel",
            self.serial,
            self.curr_version_id,
            self.channel_type,
            self.name,
        )

    def send_message(self, message: "Message"):
        timestamp = message.timestamp.timestamp()
        self.create_new_version(timestamp)
        self.game.record_bindings(
            MessageSendingBinding(
                "message_sending",  # isA
                message.sender.curr_version_id,  # sender
                timestamp,  # message: using the UNIX timestamp number as the message id
                message.message_type,  # message_type
                self.serial,  # cserial
                self.prev_version_id,  # channel0
                self.curr_version_id,  # channel1
                self.channel_type,  # channel_type
                message.content,  # message_content
            )
        )
        # broadcasting the message to all participants
        for role in self.participants:
            # Assuming all the participants read the message immediately, except the sender
            if role != message.sender:
                role.read_message(message.message_id, self.curr_version_id)


class Message:
    def __init__(
        self, message_id: float, channel, sender, content: str, message_type, private_message, turn_number, timestamp
    ):
        self.message_id = message_id
        self.channel: Channel = channel
        self.sender: Role = sender
        self.content: str = content
        self.message_type: str = message_type
        self.private_message = private_message
        self.turn_number = turn_number
        self.timestamp: datetime = timestamp


class ShipDefenceWorld:
    def __init__(self, game_id: str):
        self.game_id: str = game_id
        self.serge = SergeGame(game_id)  # interface with the Serge server for the selected game
        self.turn_numer: int = 0
        self.adjudication_start_timestamp: Optional[datetime] = None
        self.phase: str = ""
        self.timestamp: Optional[datetime] = None
        self.roles: dict[str, Role] = dict()
        self.assets: dict[str, Asset] = dict()
        self.forces: dict[str, Force] = dict()
        self.channels: dict[str, Channel] = dict()
        self.plans: dict[str, dict[int, str]] = defaultdict(dict)
        self.bindings: list[tuple] = list()

    def record_bindings(self, bindings: tuple):
        escaped_bindings = tuple(map(escaping_newline_characters, bindings))
        self.bindings.append(escaped_bindings)

    def init_game(self, info_message):
        game_data = info_message.data
        # init forces
        forces = game_data.forces.forces
        for force_data in forces:
            self.add_force(force_data)
        # init channels
        channels = game_data.channels.channels
        for channel_data in channels:
            self.add_channel(channel_data)

    def update_game(self, msg):
        data = msg.data
        # TODO update forces
        # init channels
        channels = data.channels.channels
        for channel_data in channels:
            if channel_data.uniqid not in self.channels:
                self.add_channel(channel_data)
        forces = data.forces.forces
        for force_data in forces:
            if force_data.uniqid not in self.forces:
                logger.warning("New force seen: %s", force_data.uniqid)

    def add_channel(self, channel_data):
        participants: list[Role] = list()
        for pdata in channel_data.participants:
            force = self.forces.get(pdata.forceUniqid)
            if force is None:
                logger.warning("Cannot find force <%s> to add to channel <%s>", pdata.forceUniqid, channel_data.name)
            participants.extend(force.roles.values())  # add all roles as participants
            # TODO: figure out what pdata.roles[] are for
        channel = Channel(self, channel_data.uniqid, channel_data.channelType, channel_data.name, participants)
        self.channels[channel_data.uniqid] = channel
        self.record_bindings(channel.bindings)

    def add_force(self, force_data):
        force_name = force_data.name
        force_id = force_data.uniqid
        force = Force(force_id, force_name)
        self.forces[force.serial] = force
        self.record_bindings(force.bindings)

        for role_data in force_data.roles:
            self.add_role(force, role_data)

    def add_role(self, force, role_data):
        role_type = "Human"
        if role_data.isObserver:
            role_type = "Observer"
        if role_data.isInsightViewer:
            role_type = "InsightViewer"
        if role_data.isGameControl:
            role_type = "GameControl"
        if role_data.roleId.startswith("ai-"):
            role_type = "AI"
        # special roles for the Ship Defence games
        if force.name == "Militia":
            role_type = "Simulator"
        role = Role(self, role_data.roleId, role_type, role_data.name, force)
        self.roles[role.serial] = role
        force.add_role(role)
        self.record_bindings(role.bindings)

    def add_asset(self, force, asset_id, position, asset_data):
        # Ship Defence scenario specific
        platform_type = (
            "Destroyer" if asset_id.startswith("ship-") else "Weapon" if asset_id.startswith("weapon_") else "Threat"
        )
        asset = Asset(asset_id, None, asset_data["label"], platform_type, force, position)
        self.assets[asset.serial] = asset
        force.add_asset(asset)
        self.record_bindings(asset.bindings)

    def new_turn(self, turn_number: int):
        logger.info("[New Turn: %d] – Started at %s", turn_number, self.timestamp)
        self.turn_numer = turn_number
        logger.debug("> Updating perceptions of all forces")
        for force in self.forces.values():
            self.bindings.extend(force.perception_update_bindings())

    def update_phase(self, phase: str):
        logger.info("[> Phase: %s] – %s", phase, self.timestamp)
        self.phase = phase
        self.adjudication_start_timestamp = self.timestamp if phase == "adjudication" else None

    def process_chat_message(self, msg):
        details: dict = msg.get("details")
        sender: dict = details.get("from")
        channel_id = details.get("channel")
        channel: Channel = self.channels.get(channel_id)
        if channel is None:
            logger.warning("Cannot found channel <%s>. Message will not be recorded.", channel_id)
            return
        role: Role = self.roles.get(sender.get("roleId"), None)
        timestamp = datetime.fromisoformat(details.get("timestamp"))
        # TODO check isOpen and hasBeenRead properties
        # TODO: temporarily turning off the message recording - reinstate this later
        # channel.send_message(
        #     Message(
        #         timestamp.timestamp(),  # message: using the UNIX timestamp number as the message id
        #         channel,
        #         role,
        #         msg.message.content,
        #         convert_to_type(msg.templateId),
        #         details.get("privateMessage", None),
        #         details.get("turnNumber"),
        #         timestamp,
        #     )
        # )

    def process_WA_message(self, msg):
        pass

    def end_turn_update(self, doc):
        details: dict = doc.get("details")
        sender: dict = details.get("from")
        channel_id = details.get("channel")
        channel: Channel = self.channels.get(channel_id)
        role: Role = self.roles.get(sender.get("roleId"), None)
        turn_number: int = details.get("turnNumber")
        timestamp: datetime = datetime.fromisoformat(details.get("timestamp"))
        msg_id: float = timestamp.timestamp()  # using the UNIX timestamp number as the message id
        state = doc.message.state
        # Recording the "StateOfWorld" message
        channel.create_new_version(msg_id)
        self.record_bindings(
            MessageSendingBinding(
                "message_sending",  # isA
                role.curr_version_id,  # sender
                msg_id,
                doc.messageType,  # message_type
                channel.serial,  # cserial
                channel.prev_version_id,  # channel0
                channel.curr_version_id,  # channel1
                channel.channel_type,  # channel_type
                state.name,  # message_content
            )
        )
        for force in self.forces.values():
            # Remove all perceptions to prep for the next turn's perceptions (added below)
            force.reset_perceptions()

        for force_data in state.forces:
            force_id = force_data.uniqid
            force = self.forces.get(force_id)
            force.create_new_version()  # TODO: Only create a new version if the force's assets are updated?
            for asset_data in force_data.assets:
                asset_id = asset_data.uniqid
                asset = self.assets.get(asset_id)
                asset.update_state(
                    asset_data.condition, asset_data.position, asset_data.newState.state, asset_data.newState.speedKts
                )
                plan_id = self.plans[asset_id].get(state.turn)
                act_id = f"{asset_id}/{turn_number}"
                role = force.get_the_first_role()
                asset_state_type = convert_to_type(asset.state)
                self.record_bindings(
                    EndturnActivityBinding(
                        "endturn_activity",
                        act_id,  # act
                        asset_state_type,  # act_type
                        role.curr_version_id if role is not None else None,  # role
                        plan_id,  # plan
                        asset.serial,  # aserial
                        asset.prev_version_id,  # asset0
                        asset.curr_version_id,  # asset1
                        asset.platform_type,  # asset_type
                        force.serial,  # fserial
                        force.prev_version_id,  # force0
                        force.curr_version_id,  # force1
                        asset.name,  # name
                        state.turn,  # turn_number
                        convert_to_type(asset.condition),  # condition
                        asset_state_type,  # state
                        asset.speed,  # speed
                        asset.position,  # position
                        self.adjudication_start_timestamp.isoformat(),  # startTime
                        self.timestamp.isoformat(),  # endTime
                    )
                )
                # Updating perceptions by other forces
                self.update_perception(asset, asset_data.perceptions)

    def update_perception(self, asset: Asset, perceptions: list):
        for record in perceptions:
            force_id = record.by
            # TODO: What about other properties – typeId, name, force?
            force: Force = self.forces.get(force_id)
            if force is not None:
                force.add_perception(asset)

    def process_info_message(self, msg):
        if msg.gameTurn != self.turn_numer:
            self.new_turn(msg.gameTurn)
        if msg.phase != self.phase:
            self.update_phase(msg.phase)
        self.update_game(msg)
        # self.end_turn_update(msg) ??

    def process_mapping_message(self, msg):
        # for asset_data in force_data.assets:
        #     self.add_asset(force, asset_data)
        features = msg.featureCollection.features
        for feature in features:
            self.update_feature(feature)

    def update_feature(self, feature):
        # only process "Point" features
        if feature.geometry.type != "Point":
            return
        pos_lon, pos_lat = feature.geometry.coordinates
        # copy the properties dict
        properties = dict(feature.properties)
        _type = properties.pop("_type")
        if _type != "MilSymRenderer":
            return
        force_id: str = properties.pop("force")
        feature_id: str = properties.pop("id")
        # TODO Hack to be removed: assign force ID to threats
        if not feature_id.startswith("ship-") and not feature_id.startswith("weapon_"):
            force_id = "f-militia"
        force = self.forces.get(force_id)
        if feature_id not in force.assets:
            # create the asset
            self.add_asset(force, feature_id, (pos_lat, pos_lon), properties)

    def process_custom_message(self, msg: dict):
        if msg.templateId == "chat":
            self.process_chat_message(msg)
        elif msg.templateId == "WA Message":
            self.process_WA_message(msg)

    def run(self):
        # load messages from the Serge server
        cached_messages_file = Path(f"provenance/outputs/{self.game_id}.json")
        if cached_messages_file.exists():
            with cached_messages_file.open() as f:
                messages = json.load(f)
                logger.debug("Loaded %d messages from %s", len(messages), cached_messages_file)
        else:
            messages = self.serge.get_new_messages()
            logger.debug("Retrieved %d messages from the game %s", len(messages), self.game_id)
            with cached_messages_file.open("w") as f:
                json.dump(messages, f, indent=2)

        # process messages
        messages = munchify(messages)
        # add timestamp to the messages
        messages = list(map(add_timestamp_from_id, messages))
        # initialise the game world
        first_info_message = messages[0]
        assert first_info_message.messageType == "InfoMessage"  # expecting the first message to be an InfoMessage
        self.init_game(first_info_message)
        while messages:
            msg = messages.pop(0)
            print(msg.messageType, msg._id)
            self.timestamp = msg.timestamp
            if msg.messageType == "InfoMessage":
                self.process_info_message(msg)
            elif msg.messageType == "MappingMessage":
                while messages and messages[0].messageType == "MappingMessage":
                    # consecutive MappingMessage overwrites the previous one; we only need the last one
                    logger.debug("Ignoring the MappingMessage at %s", msg._id)
                    msg = messages.pop(0)
                self.process_mapping_message(msg)
            elif msg.messageType == "CustomMessage":
                self.process_custom_message(msg)
            else:
                logger.warning("Unknown message type: %s", msg.messageType)

    # save the bindings to a CSV file
    def write_bindings(self, path: Path):
        with path.open("w") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(self.bindings)


def add_timestamp_from_id(msg):
    msg.timestamp = datetime.fromisoformat(msg._id)
    return msg


def escaping_newline_characters(value: str) -> str:
    return value.replace("\n", "\\n") if value is not None and isinstance(value, str) else value


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Path initialisations
    csv_folder = Path("provenance/csv")
    target_folder = Path("provenance/outputs")

    game_id = "wargame-lzind2c4"
    log_file_handler = logging.FileHandler(target_folder / f"{game_id}.log")
    logger.addHandler(log_file_handler)

    world = ShipDefenceWorld(game_id)

    # load and process game messages
    world.run()

    # export the bindings
    world.write_bindings(csv_folder / f"{game_id}.csv")
