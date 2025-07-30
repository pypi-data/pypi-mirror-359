# Copyright 2025 © BeeAI a Series of LF Projects, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any

import acp_sdk.models as acp_models

from beeai_framework.backend import AssistantMessage, CustomMessage, Message, Role, SystemMessage, UserMessage


def acp_msg_to_framework_msg(role: Role, content: str) -> Message[Any]:
    match role:
        case Role.USER:
            return UserMessage(content)
        case Role.ASSISTANT:
            return AssistantMessage(content)
        case Role.SYSTEM:
            return SystemMessage(content)
        case _:
            return CustomMessage(role=role, content=content)


def acp_msgs_to_framework_msgs(messages: list[acp_models.Message]) -> list[Message[Any]]:
    return [
        acp_msg_to_framework_msg(Role(message.parts[0].role), str(message))  # type: ignore[attr-defined]
        for message in messages
    ]
