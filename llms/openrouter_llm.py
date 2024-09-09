import json
from os import getenv
from typing import Any

import requests
from openai import NOT_GIVEN, OpenAI

from lightlang.llms.config.openrouter_config import OPENROUTER_MODEL_CONFIG
from lightlang.llms.utils import get_user_message
from lightlang.models import ChatMessage

OPENROUTER_BASE = "https://openrouter.ai"
OPENROUTER_API_BASE = f"{OPENROUTER_BASE}/api/v1"


class OpenRouterLLM:
    """Interface for interacting with models via the OpenRouter API."""

    # Global settings that can be overridden by instance settings
    config = {"MODELS": OPENROUTER_MODEL_CONFIG}
    client = OpenAI(
        base_url=OPENROUTER_API_BASE,
        api_key=getenv("OPENROUTER_API_KEY"),
    )

    def __init__(
        self,
        client: OpenAI | None = None,
        config: dict[str, dict[str, Any]] | None = None,
        **settings,
    ):
        """Initialize the OpenRouterLLM instance.

        The settings keyword arguments can (and usually should) include the following:
        - model: The model to use for completions (e.g., "openai/gpt-4o-mini").
        - temperature: The sampling temperature to use for completions.
        """
        if client is not None:
            self.client = client
        if config is not None:
            self.config = config
        self.settings = settings
        self.stream_status = "NOT_STREAMING"

    def _get_provider_param(self, model):
        try:
            model_config = self.config["MODELS"][model]
            return {"provider": {"order": list(model_config["providers"].keys())}}  # type: ignore
        except KeyError:
            return {}

    def _get_settings(self, stream, messages, model, temperature, **kwargs):
        # If messages is a string (single prompt), convert it to a list of ChatMessage
        if isinstance(messages, str):
            messages = [get_user_message(messages)]

        settings = {"model": model, "temperature": temperature}
        settings |= {"messages": messages, "stream": stream} | kwargs

        # Remove NOT_GIVEN values
        settings = {k: v for k, v in settings.items() if v is not NOT_GIVEN}

        # Merge instance settings with provided settings
        settings = self.settings | settings

        # Add providers (if configured) but only if they are not already set
        if "provider" not in settings.get("extra_body", {}):
            if provider_param := self._get_provider_param(settings.get("model")):
                settings.setdefault("extra_body", {}).update(provider_param)
        return settings

    def get_model_name(self) -> str | None:
        return self.settings.get("model")

    def invoke(
        self,
        messages: str | list[ChatMessage],
        model=NOT_GIVEN,
        temperature=NOT_GIVEN,
        **kwargs,
    ):
        settings = self._get_settings(False, messages, model, temperature, **kwargs)
        completion = self.client.chat.completions.create(**settings)
        return completion.choices[0].message.content

    def stream(
        self,
        messages: str | list[ChatMessage],
        model=NOT_GIVEN,
        temperature=NOT_GIVEN,
        **kwargs,
    ):
        settings = self._get_settings(True, messages, model, temperature, **kwargs)
        completion = self.client.chat.completions.create(**settings)
        self.stream_status = "STARTED"
        for chunk in completion:
            if chunk.choices:
                # Can be empty for last chunk if stream_options: {"include_usage": true}
                if content := chunk.choices[0].delta.content:
                    if self.stream_status == "STARTED":
                        self.stream_status = "FIRST_CHUNK"
                    else:
                        self.stream_status = "IN_PROGRESS"
                    yield content
        self.stream_status = "NOT_STREAMING"


def format_prompt(prompt: str) -> list[ChatMessage]:
    return [get_user_message(prompt)]


def get_available_models():
    try:
        response = requests.get(f"{OPENROUTER_API_BASE}/models")
        response.raise_for_status()
        models = json.loads(response.text)["data"]
        return [model["id"] for model in models]
    except requests.exceptions.RequestException as e:
        raise e


if __name__ == "__main__":
    llm = OpenRouterLLM(model="openai/gpt-4o-mini")
    response = llm.stream(
        model="mistralai/mistral-7b-instruct:free",
        messages=format_prompt("What is the capital of France?"),
    )
    for content in response:
        if content:
            print(content, end="")
