import abc
from typing import Any

import litellm
from openai.types.chat import ChatCompletionToolParam


class BaseLLMClient(abc.ABC):
    """Base class for LLM clients."""

    def __init__(self, *, model: str, api_key: str | None = None, api_base: str | None = None, api_version: str | None = None):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.api_version = api_version

    @abc.abstractmethod
    async def completion(self, messages: list[Any], tools: list[ChatCompletionToolParam] | None = None, tool_choice: str = "auto") -> Any:  # noqa: ANN401
        """Perform a completion request to the LLM."""


class LiteLLMClient(BaseLLMClient):
    async def completion(self, messages: list[Any], tools: list[ChatCompletionToolParam] | None = None, tool_choice: str = "auto") -> Any:  # noqa: ANN401
        """Perform a completion request to the Litellm API."""
        return await litellm.acompletion(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            api_version=self.api_version,
            api_key=self.api_key,
            api_base=self.api_base,
            stream=True,
        )
