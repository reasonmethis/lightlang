import os
from typing import Any, Literal

from openai import OpenAI

from lightlang.llms.config.model_config import (
    DEFAULT_MODEL_CONFIG_BY_PROVIDER,
    DEFAULT_MODEL_CONFIG_BY_PROVIDER_AND_MODEL,
)
from lightlang.llms.config.provider_config import DEFAULT_PROVIDER_CONFIGS
from lightlang.llms.utils import get_user_message
from lightlang.types.common import ChatMessage, LLMProvider
from lightlang.types.models import LLMResponse, LLMResponseChunk
from lightlang.types.utils import is_allowed_llm_provider


class LLM:
    """LLM from any provider, offering a common interface."""

    _default_provider: LLMProvider | None = None

    def __init__(
        self,
        model: str,
        *,
        provider: LLMProvider | str | None = None, # str is so users don't need to cast
        api_key: str | None = None,
        temperature: float | None = None,
        model_config: dict | None = None,
        provider_config: dict | None = None,
        provider_client: Any | None = None,
    ):
        self._provider = provider or self._default_provider
        self._model = model

        # If no provider is specified or set as default, raise an error
        if self._provider is None:
            raise ValueError("No LLM provider specified and no default provider set.")
        
        # Type guard the provider
        if not is_allowed_llm_provider(self._provider):
            raise ValueError(f"Unsupported LLM provider: {self._provider}")

        # Merge the given provider config with the default provider config
        default_provider_config = DEFAULT_PROVIDER_CONFIGS.get(self._provider, {})
        self._provider_config = default_provider_config | (provider_config or {})
        self._api_type = self._provider_config.get("api_type")

        # Merge the given model config with the default model config
        self._model_config = (
            DEFAULT_MODEL_CONFIG_BY_PROVIDER.get(self._provider, {})
            | DEFAULT_MODEL_CONFIG_BY_PROVIDER_AND_MODEL.get(self._provider, {}).get(
                model, {}
            )
            | (model_config or {})
            | {"model": model}
        )

        # If temperature is provided explicitly, add it to the model config
        if temperature is not None:
            self._model_config["temperature"] = temperature

        # If a provider client is provided, use it; otherwise, create a new client
        if provider_client is not None:
            self._provider_client = provider_client
        elif self._api_type == "openai":
            self._provider_client = OpenAI(
                base_url=self._provider_config["base_url"],
                api_key=api_key or os.getenv(self._provider_config["api_key_env_var"]),
            )
        else:
            raise NotImplementedError(f"Unsupported provider type: {self._api_type}")

        # Initialize state
        self.stream_status: Literal[
            "NOT_STREAMING", "STARTED", "FIRST_CHUNK", "IN_PROGRESS"
        ] = "NOT_STREAMING"
        self.stream_content: str = ""  # Response so far or on last stream request

    @property
    def provider(self) -> LLMProvider:
        return self._provider # type: ignore # mypy bug (was type-guarded)
    
    @property
    def model(self) -> str:
        return self._model
    
    def invoke(self, messages: str | list[ChatMessage]) -> LLMResponse:
        """Invoke the model with the given messages."""
        # Construct the arguments for the provider's API
        args = self._get_call_args(messages)

        # Different invocation logic for different providers
        if self._api_type == "openai":
            completion = self._provider_client.chat.completions.create(
                **args, stream=False
            )
            return LLMResponse(completion)
        else:
            raise Exception("LLM class: This should be unreachable.")

    def stream(self, messages: str | list[ChatMessage]):
        """Stream the model's response with the given messages."""
        # Construct the arguments for the provider's API
        args = self._get_call_args(messages)

        # Initialize the stream state
        self.stream_status = "STARTED"
        self.stream_content = ""

        # Different streaming logic for different providers
        if self._api_type == "openai":
            for chunk in self._provider_client.chat.completions.create(
                **args, stream=True
            ):
                response_chunk = LLMResponseChunk(chunk)
                self._update_stream_state(response_chunk)
                yield response_chunk
        else:
            raise Exception("LLM class: This should be unreachable.")

        self.stream_status = "NOT_STREAMING"

    @classmethod
    def set_default_provider(cls, provider: LLMProvider):
        """Set the default provider for all LLM instances."""
        cls._default_provider = provider

    def _update_stream_state(self, response_chunk: LLMResponseChunk):
        if response_chunk.content is not None:
            # Accumulate the response text so far and update the stream status
            self.stream_content += response_chunk.content
            self.stream_status = (
                "FIRST_CHUNK" if self.stream_status == "STARTED" else "IN_PROGRESS"
            )

    def _get_call_args(self, messages: str | list[ChatMessage]):
        # If messages is a string (single prompt), convert it to a list of ChatMessage
        if isinstance(messages, str):
            messages = [get_user_message(messages)]

        # Create the full settings depending on the provider type
        if self._api_type == "openai":
            return self._model_config | {"messages": messages}
        else:
            raise NotImplementedError(f"Unsupported provider type: {self._api_type}")


if __name__ == "__main__":
    # Example usage
    # NOTE: Run this script as a module: python -m lightlang.llms.llm
    llm = LLM(provider="openrouter", model="openai/gpt-4o-mini")  # Option 1
    # llm = LLM(provider="openai", model="gpt-4o-mini")  # Option 2

    STREAM = False
    if STREAM:
        response = llm.stream("What is the capital of France?")
        for chunk in response:
            if chunk.content:
                print(chunk.content, end="")
    else:
        response = llm.invoke("What is the capital of France?")
        print(response.content)
