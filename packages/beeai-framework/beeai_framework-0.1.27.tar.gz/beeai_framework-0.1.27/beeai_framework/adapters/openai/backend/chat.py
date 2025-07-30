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


import os

from typing_extensions import Unpack

from beeai_framework.adapters.litellm import utils
from beeai_framework.adapters.litellm.chat import LiteLLMChatModel
from beeai_framework.backend.chat import ChatModelKwargs
from beeai_framework.backend.constants import ProviderName
from beeai_framework.logger import Logger

logger = Logger(__name__)


class OpenAIChatModel(LiteLLMChatModel):
    """
    A chat model implementation for the OpenAI provider, leveraging LiteLLM.
    """

    @property
    def provider_id(self) -> ProviderName:
        """The provider ID for OpenAI."""
        return "openai"

    def __init__(
        self,
        model_id: str | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        text_completion: bool | None = False,
        **kwargs: Unpack[ChatModelKwargs],
    ) -> None:
        """
        Initializes the OpenAIChatModel.

        Args:
            model_id: The ID of the OpenAI model to use. If not provided,
                it falls back to the OPENAI_CHAT_MODEL environment variable,
                and then defaults to 'gpt-4o'.
            **kwargs: A dictionary of settings to configure the provider.
        """
        super().__init__(
            model_id if model_id else os.getenv("OPENAI_CHAT_MODEL", "gpt-4o"),
            provider_id="text-completion-openai" if text_completion else "openai",
            **kwargs,
        )
        self._assert_setting_value("api_key", api_key, envs=["OPENAI_API_KEY"])
        self._assert_setting_value(
            "base_url", base_url, envs=["OPENAI_API_BASE"], aliases=["api_base"], allow_empty=True
        )
        self._settings["extra_headers"] = utils.parse_extra_headers(
            self._settings.get("extra_headers"), os.getenv("OPENAI_API_HEADERS")
        )
