from typing import Any

from pydantic import BaseModel

from lightlang.types.common import ChatCompletion, ChatCompletionChunk


class Doc(BaseModel):
    """Pydantic-compatible version of Langchain's Document."""

    text: str
    metadata: dict[str, Any]


class LLMResponse:
    """Response from a language model."""

    def __init__(self, chat_completion: ChatCompletion):
        self.chat_completion = chat_completion
        self.content = self.chat_completion.choices[0].message.content

    def to_json(self) -> str:
        return self.chat_completion.model_dump_json()


class LLMResponseChunk:
    """A chunk of a language model's streaming response."""

    def __init__(self, chat_completion_chunk: ChatCompletionChunk):
        self.chat_completion_chunk = chat_completion_chunk

        try:
            self.content = self.chat_completion_chunk.choices[0].delta.content
        except IndexError:
            # choices can be empty for last chunk if stream_options: {"include_usage": true}
            self.content = None

    def to_json(self) -> str:
        return self.chat_completion_chunk.model_dump_json()
