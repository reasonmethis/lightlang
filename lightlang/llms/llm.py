from typing import Any, Literal

from openai import OpenAI

from lightlang.llms.config.model_config import (
    DEFAULT_MODEL_CONFIG_BY_PROVIDER,
    DEFAULT_MODEL_CONFIG_BY_PROVIDER_AND_MODEL,
)
from lightlang.llms.config.provider_config import DEFAULT_PROVIDER_CONFIGS
from lightlang.llms.utils import get_user_message
from lightlang.models import ChatCompletion, ChatMessage

LLMProvider = Literal["openai", "openrouter"]


class LLM:
    """LLM from any provider, offering a common interface."""

    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        *,
        temperature: float | None = None,
        model_config: dict | None = None,
        provider_config: dict | None = None,
        provider_client: Any | None = None,
    ):
        self._provider = provider
        self._model = model

        # Merge the given provider config with the default provider config
        default_provider_config = DEFAULT_PROVIDER_CONFIGS.get(provider, {})
        self._provider_config = default_provider_config | (provider_config or {})
        self._api_type = self._provider_config.get("api_type")

        # Merge the given model config with the default model config
        x = DEFAULT_MODEL_CONFIG_BY_PROVIDER.get(provider, {})
        y = DEFAULT_MODEL_CONFIG_BY_PROVIDER_AND_MODEL.get(provider, {}).get(model, {})
        self._model_config = x | y | (model_config or {})

        # If temperature is provided explicitly, add it to the model config
        if temperature is not None:
            self._model_config["temperature"] = temperature

        # If a provider client is provided, use it; otherwise, create a new client
        if provider_client is not None:
            self._provider_client = provider_client
        elif self._api_type == "openai":
            self._provider_client = OpenAI(
                base_url=self._provider_config["base_url"],
                api_key=self._provider_config["api_key"],
            )
        # Initialize state
        self.stream_status = "NOT_STREAMING"

    def invoke(self, messages: str | list[ChatMessage]) -> ChatCompletion:
        """Invoke the model with the given messages."""
        settings = self._get_settings(messages, stream=False)
        if isinstance(self._provider_client, OpenAI):  # _api_type == "openai"
            completion: ChatCompletion = self._provider_client.chat.completions.create(
                **settings
            )
            return completion
        else:
            raise Exception("LLM class: This should be unreachable.")

    def invoke_txt(self, messages: str | list[ChatMessage]) -> str:
        """Invoke the model with the given messages and return just the text."""
        completion = self.invoke(messages)
        return completion.choices[0].message.content

    def _get_settings(self, messages: str | list[ChatMessage], stream: bool):
        # If messages is a string (single prompt), convert it to a list of ChatMessage
        if isinstance(messages, str):
            messages = [get_user_message(messages)]

        # Create the full settings depending on the provider type
        if self._api_type == "openai":
            return self._model_config | {"messages": messages, "stream": stream}
        else:
            raise NotImplementedError(f"Unsupported provider type: {self._api_type}")
