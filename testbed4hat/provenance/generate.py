__package__ = "testbed4hat.provenance"

from collections import defaultdict, namedtuple
import csv
from datetime import datetime
import json
import logging
from pathlib import Path
import re
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
MissileBinding = namedtuple(
    "MissileBinding",
    [
        "isA",
        "mserial",
        "missile",
        "missile_type",
        "fserial",
        "force",
        "force_name",
        "name",
        "position",
        "velocity",
        "target",
    ],
)
MissileLaunchBinding = namedtuple(
    "MissileLaunchBinding",
    [
        "isA",
        "ship",
        "missile_0",
        "missile_1",
        "missile_type",
        "position",
        "velocity",
        "target",
        "wa",
    ],
)
TargetSuggestionBinding = namedtuple(
    "TargetSuggestionBinding",
    [
        "isA",
        "sender",
        "wa",
        "wa_type",
        "asset",
        "target",
        "weapon",
    ],
)
TargetingAmendmentBinding = namedtuple(
    "TargetingAmendmentBinding",
    [
        "isA",
        "role",
        "wa_0",
        "wa_1",
        "wa_type",
        "asset",
        "target",
        "weapon",
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
    def __init__(self, asset_id, name, platform_type, force, position):
        super().__init__(asset_id)
        self.contact_id: str | None = None
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


class Missile(Asset):
    def __init__(self, asset_id, name, missile_type, force, position, velocity, target_id: str, parent: Asset = None):
        # threat, threat_type, fserial, force, force_name, name, position, velocity, target
        super().__init__(asset_id, name, missile_type, force, position)
        self.speed = velocity
        self.target_id: str | None = target_id
        self.parent: Asset | None = parent

    @property
    def bindings(self) -> MissileBinding:
        return MissileBinding(
            "missile",
            self.serial,  # mserial
            self.curr_version_id,  # missile
            self.platform_type,  # missile_type
            self.force.serial,  # fserial
            self.force.curr_version_id,  # force
            self.force.name,  # force_name
            self.name,
            self.position,
            self.speed,
            self.target_id,  # target
        )

    def launch(self, position, velocity, target_id: str, wa_id: str):
        assert self.parent is not None  # require a parent to launch
        self.create_new_version()
        self.position = position
        self.speed = velocity
        self.target_id = target_id
        return MissileLaunchBinding(
            "missile_launch",
            self.parent.curr_version_id,  # ship
            self.prev_version_id,  # missile_0
            self.curr_version_id,  # missile_1
            self.platform_type,  # missile_type
            self.position,  # position
            self.speed,  # velocity
            self.target_id,  # target
            wa_id,  # wa
        )


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

    def remove_asset(self, asset: Asset):
        if asset.serial in self.assets:
            del self.assets[asset.serial]

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
    def __init__(self, channel: Channel, sender: Role, metadata: dict, content: dict):
        timestamp = datetime.fromisoformat(metadata.get("timestamp"))
        self.message_id: float = timestamp.timestamp()  # using the UNIX timestamp number as the message id
        self.channel: Channel = channel
        self.sender: Role = sender
        self.message_type: str | None = None
        self.private_message = metadata.get("privateMessage", None)
        self.turn_number = metadata.get("turnNumber")
        self.timestamp: datetime = timestamp


class ChatMessage(Message):
    def __init__(self, channel: Channel, sender: Role, metadata: dict, content: dict):
        super().__init__(channel, sender, metadata, content)
        self.message_type = "ChatMessage"
        self.content: str = content.get("content")


class WAMessage(Message):
    def __init__(self, channel: Channel, sender: Role, metadata: dict, content: dict):
        super().__init__(channel, sender, metadata, content)
        self.message_type = "WAMessage"
        self.history = metadata.collaboration
        # find the ship that received this targeting suggestion
        self.asset_name = channel.name
        self.target_id = content.Threat.ID
        self.weapon = content.Weapon


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
        # missiles seen on the map in the current turn
        self.missile_seen: dict[str, set[str]] = defaultdict(set)  # force_id -> {missile_id}
        # actions released their corresponding WA message id (in a list to accommodate multiple same actions)
        self.actions: dict[tuple, list[str]] = defaultdict(list)

        self.bindings: list[tuple] = list()  # list of provenance bindings

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

    def new_turn(self, turn_number: int):
        logger.info("[New Turn: %d] – Started at %s", turn_number, self.timestamp)

        # resetting the ephemeral states that should not persist across game turns
        self.missile_seen = defaultdict(set)

        self.turn_numer = turn_number
        logger.debug("> Updating perceptions of all forces")
        for force in self.forces.values():
            self.bindings.extend(force.perception_update_bindings())

    def update_phase(self, phase: str):
        logger.info("[> Phase: %s] – %s", phase, self.timestamp)
        self.phase = phase
        self.adjudication_start_timestamp = self.timestamp if phase == "adjudication" else None

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
        features = msg.featureCollection.features
        for feature in features:
            # only process "Point" features
            if feature.geometry.type == "Point":
                self.update_feature(feature)

    def update_ship(self, force: Force, ship_id: str, position, properties: dict):
        if ship_id not in force.assets:
            ship = Asset(ship_id, properties["label"], "Destroyer", force, position)
            self.assets[ship.serial] = ship
            force.add_asset(ship)
            self.record_bindings(ship.bindings)
        else:
            # TODO: update any changes to the ship
            pass

    def find_asset_by_name(self, name: str | None) -> Asset | None:
        if name is None:
            return None
        for force in self.forces.values():
            for asset in force.assets.values():
                if asset.name == name:
                    return asset
        return None

    def find_asset_by_id(self, asset_id: str | None) -> Asset | None:
        if asset_id is None:
            return None
        for force in self.forces.values():
            for asset in force.assets.values():
                if asset.serial == asset_id:
                    return asset
        return None

    def update_threat(self, force: Force, missile_id: str, position, properties: dict):
        if missile_id not in force.assets:
            # create the Missile
            missile_type = properties.get("Detected type", "UndeterminedMissile")
            velocity = properties.get("Velocity", None)
            target_name: str | None = properties.get("Ship Targeted", None)

            target = self.find_asset_by_name(target_name)
            missile = Missile(
                missile_id,
                properties["label"],
                convert_to_type(missile_type),
                force,
                position,
                velocity,
                target.serial,
                None,
            )
            self.assets[missile.serial] = missile
            force.add_asset(missile)
            self.record_bindings(missile.bindings)
        else:
            # TODO: update any changes to the missile
            missile = force.assets[missile_id]
            missile.update_state(properties.get("heath", None), position, None, properties.get("Velocity", None))

    def update_weapon(self, force: Force, missile_id: str, position, properties: dict):
        if missile_id not in self.assets:
            # create the Missile
            missile_type = properties.get("type", "UndeterminedMissile")
            parent_name = properties.get("Launched by", None)
            parent = self.find_asset_by_name(parent_name)
            target_id: str | None = properties.get("Threat Targeted", None)
            # hack to reconcile the shortened threat ID
            target_id = target_id[target_id.index("_") + 1 :]
            missile = Missile(
                missile_id,
                properties["label"],
                convert_to_type(missile_type),
                force,
                None,  # this and the below properties will be added in the launch event below
                None,
                None,
                parent,
            )
            self.assets[missile.serial] = missile
            force.add_asset(missile)
            self.record_bindings(missile.bindings)

            # create a launch event and link it with the WA message that released the weapon
            try:
                wa_id = self.actions[(parent.serial, missile_type, target_id)].pop(0)
            except IndexError:
                logger.warning(
                    "No WA message recorded for for %s's weapon %s (%s) targeting %s",
                    parent.serial,
                    missile_id,
                    missile_type,
                    target_id,
                )
                logger.debug("Currently recorded actions: %s", self.actions)
                wa_id = None
            self.record_bindings(missile.launch(position, properties.get("Velocity", None), target_id, wa_id))
        else:
            # TODO: update any changes to the missile
            missile = force.assets[missile_id]
            missile.update_state(properties.get("heath", None), position, None, None)

    def update_feature(self, feature):
        # copy the properties dict
        properties = dict(feature.properties)

        _type = properties.pop("_type")
        if _type != "MilSymRenderer":
            # We only process MilSymRenderer objects in this scenario
            return

        pos_lon, pos_lat = feature.geometry.coordinates
        force_id: str = properties.pop("force")
        feature_id: str = properties.pop("id")
        force = self.forces.get(force_id)

        if feature_id.startswith("ship-"):
            self.update_ship(force, feature_id, f"{pos_lat},{pos_lon}", properties)
        else:
            # must be a missile; add it to the list of missiles seen in this round
            self.missile_seen[force_id].add(feature_id)
            # determine weapon or threat
            if feature_id.startswith("weapon_"):
                self.update_weapon(force, feature_id, f"{pos_lat},{pos_lon}", properties)
            else:
                self.update_threat(force, feature_id, f"{pos_lat},{pos_lon}", properties)

        # TODO: remove missile(s) not seen in this round
        pass

    def process_WA_message(self, msg):
        # Generate bindings for the various steps in the message's lifecyle
        # 1. Targetting suggesting
        asset = self.find_asset_by_name(msg.asset_name)
        target = self.find_asset_by_id(msg.target_id)
        current_id = msg.message_id

        self.record_bindings(
            TargetSuggestionBinding(
                "targeting_suggestion",  # targeting_suggestion
                msg.sender.curr_version_id,  # sender
                current_id,  # wa
                "AISuggestion" if msg.sender.serial == "ai-assistant" else "ManualAssignment",  # wa_type
                asset.curr_version_id,  # asset
                target.curr_version_id,  # target
                msg.weapon,  # weapon
            )
        )
        # 2. Amendments if any
        if "feedback" in msg.history:
            previous_id = current_id
            p_action = re.compile(r"^\[(?P<action>\w+)\]")
            for feedback in msg.history.feedback:
                role = self.roles.get(feedback.fromId)
                timestamp = datetime.fromisoformat(feedback.date)
                current_id = timestamp.timestamp()
                m_action = p_action.match(feedback.feedback)
                wa_type = (
                    m_action.group("action") + "WeaponAssignment"
                    if m_action is not None
                    else "UndeterminedWeaponAssignment"
                )
                self.record_bindings(
                    TargetingAmendmentBinding(
                        "targeting_amendment",  # isA
                        role.curr_version_id,  # role
                        previous_id,  # wa_0
                        current_id,  # wa_1
                        wa_type,  # wa_type
                        asset.curr_version_id,  # asset
                        target.curr_version_id,  # target
                        msg.weapon,  # weapon
                    )
                )

            if msg.history.status == "Released":
                # 3. Remember WA message ID for the assignment
                self.actions[(asset.serial, msg.weapon, target.serial)].append(current_id)
                logger.debug("Weapon to release (%s): %s", current_id, (asset.serial, msg.weapon, target.serial))

    def process_custom_message(self, msg: dict):
        details: dict = msg.get("details")
        sender: dict = details.get("from")
        channel_id = details.get("channel")
        channel: Channel = self.channels.get(channel_id)
        if channel is None:
            logger.warning("Cannot found channel <%s>. Message will not be recorded.", channel_id)
            return
        role_id = sender.get("roleId")
        # TODO: Hack for legacy malformed WA messages due to the wrong template (which have already been fixed)
        if "roleId" in role_id:
            role_id = role_id.get("roleId")
        role: Role = self.roles.get(role_id, None)

        if msg.templateId == "chat":
            message = ChatMessage(channel, role, details, msg.message)
            # TODO: temporarily turning off the message recording - reinstate this later
            # channel.send_message(message)
        elif msg.templateId == "WA Message":
            wa_msg = WAMessage(channel, role, details, msg.message)
            self.process_WA_message(wa_msg)

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

    game_id = "wargame-lzudwjdd"
    log_file_handler = logging.FileHandler(target_folder / f"{game_id}.log")
    logger.addHandler(log_file_handler)

    world = ShipDefenceWorld(game_id)

    # load and process game messages
    world.run()

    # export the bindings
    world.write_bindings(csv_folder / f"{game_id}.csv")
