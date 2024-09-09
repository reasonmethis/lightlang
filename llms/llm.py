from typing import Literal

from lightlang.llms.config.model_config import (
    DEFAULT_MODEL_CONFIG_BY_PROVIDER,
    DEFAULT_MODEL_CONFIG_BY_PROVIDER_AND_MODEL,
)
from lightlang.llms.config.provider_config import DEFAULT_PROVIDER_CONFIGS
from lightlang.llms.utils import get_user_message
from lightlang.models import ChatMessage

LLMProvider = Literal["openai", "openrouter"]


class LLM:
    """LLM from any provider, offering a common interface."""

    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        *,
        temperature: float | None = None,
        provider_config: dict | None = None,
        model_config: dict | None = None,
    ):
        self._provider = provider
        self._model = model

        # Merge the given provider config with the default provider config
        default_provider_config = DEFAULT_PROVIDER_CONFIGS.get(provider, {})
        self._provider_config = default_provider_config | (provider_config or {})

        # Merge the given model config with the default model config
        x = DEFAULT_MODEL_CONFIG_BY_PROVIDER.get(provider, {})
        y = DEFAULT_MODEL_CONFIG_BY_PROVIDER_AND_MODEL.get(provider, {}).get(model, {})
        self._model_config = x | y | (model_config or {})

        # If temperature is provided explicitly, add it to the model config
        if temperature is not None:
            self._model_config["temperature"] = temperature

        # Initialize state
        self.stream_status = "NOT_STREAMING"

    def invoke(self, messages: str | list[ChatMessage]):
        """Invoke the model with the given messages."""
        pass
        # TODO: along the lines of the following
        # settings = self._get_settings(False, messages, model, temperature, **kwargs)
        # completion = self.client.chat.completions.create(**settings)
        # return completion.choices[0].message.content

    def _get_settings(self, messages, stream):
        # If messages is a string (single prompt), convert it to a list of ChatMessage
        if isinstance(messages, str):
            messages = [get_user_message(messages)]
        # TODO: finish along the lines of the following
        # settings = {"model": model, "temperature": temperature}
        # settings |= {"messages": messages, "stream": stream} | kwargs
