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

from typing import Any, Self

try:
    import wikipediaapi  # type: ignore
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "Optional module [wikipedia] not found.\nRun 'pip install \"beeai-framework[wikipedia]\"' to install."
    ) from e

from pydantic import BaseModel, Field

from beeai_framework.context import RunContext
from beeai_framework.emitter.emitter import Emitter
from beeai_framework.tools.search import SearchToolOutput, SearchToolResult
from beeai_framework.tools.tool import Tool
from beeai_framework.tools.types import ToolRunOptions


class WikipediaToolInput(BaseModel):
    query: str = Field(description="Name of the Wikipedia page.")
    full_text: bool = Field(
        description="If set to true, it will return the full text of the page instead of its short summary.",
        default=False,
    )


class WikipediaToolResult(SearchToolResult):
    pass


class WikipediaToolOutput(SearchToolOutput):
    pass


class WikipediaTool(Tool[WikipediaToolInput, ToolRunOptions, WikipediaToolOutput]):
    name = "Wikipedia"
    description = "Search factual and historical information, including biography, history, politics, geography, society, culture, science, technology, people, animal species, mathematics, and other subjects."  # noqa: E501
    input_schema = WikipediaToolInput

    def __init__(self, options: dict[str, Any] | None = None, *, language: str = "en") -> None:
        super().__init__(options)
        self.client = wikipediaapi.Wikipedia(user_agent="beeai-framework https://github.com/i-am-bee/beeai-framework")
        self._language = language

    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(
            namespace=["tool", "search", "wikipedia"],
            creator=self,
        )

    async def _run(
        self, input: WikipediaToolInput, options: ToolRunOptions | None, context: RunContext
    ) -> WikipediaToolOutput:
        page_py = self.client.page(input.query)

        if not page_py.exists():
            return WikipediaToolOutput([])

        if self._language in page_py.langlinks:
            page_py = page_py.langlinks[self._language]

        description_output = page_py.text if input.full_text else page_py.summary

        return WikipediaToolOutput(
            [
                WikipediaToolResult(
                    title=page_py.title or input.query,
                    description=description_output or "",
                    url=page_py.fullurl or "",
                )
            ]
        )

    async def clone(self) -> Self:
        cloned = await super().clone()
        cloned._language = self._language
        return cloned
