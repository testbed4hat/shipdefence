from collections import namedtuple

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
AssetUpdateBinding = namedtuple(
    "AssetUpdateBinding",
    [
        "isA",
        "asset_0",
        "asset_1",
        "asset_type",
        "name",
        "position",
        "speed",
        "condition",
        "state",
        "turn",
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
