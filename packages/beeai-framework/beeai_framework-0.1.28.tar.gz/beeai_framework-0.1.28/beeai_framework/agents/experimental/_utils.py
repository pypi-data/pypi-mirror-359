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


from beeai_framework.agents.experimental.prompts import (
    RequirementAgentSystemPromptInput,
    RequirementAgentToolTemplateDefinition,
)
from beeai_framework.agents.experimental.types import RequirementAgentRequest
from beeai_framework.backend import SystemMessage
from beeai_framework.template import PromptTemplate
from beeai_framework.utils.strings import to_json


def _create_system_message(
    *, template: PromptTemplate[RequirementAgentSystemPromptInput], request: RequirementAgentRequest
) -> SystemMessage:
    return SystemMessage(
        template.render(
            tools=[
                RequirementAgentToolTemplateDefinition.from_tool(tool, allowed=tool in request.allowed_tools)
                for tool in request.tools
            ],
            final_answer_name=request.final_answer.name,
            final_answer_schema=to_json(
                request.final_answer.input_schema.model_json_schema(mode="validation"), indent=2
            )
            if request.final_answer.custom_schema
            else None,
            final_answer_instructions=request.final_answer.instructions,
        )
    )
