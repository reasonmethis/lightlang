from typing import Any

from pydantic import BaseModel

from lightlang.types.common import (
    ChatCompletion,
    ChatCompletionChunk,
    TaskEventData,
    TaskEventType,
)


class Doc(BaseModel):
    """Pydantic-compatible version of Langchain's Document."""

    text: str
    metadata: dict[str, Any]


class LLMResponse:
    """Response from a language model."""

    def __init__(self, chat_completion: ChatCompletion):
        self.chat_completion = chat_completion
        self.content = self.chat_completion.choices[0].message.content

    def jsonify_full_llm_response(self) -> str:
        return self.chat_completion.model_dump_json()


class LLMResponseChunk:
    """A chunk of a language model's streaming response."""

    def __init__(self, chat_completion_chunk: ChatCompletionChunk | None = None):
        self.chat_completion_chunk = chat_completion_chunk

        try:
            self.content = self.chat_completion_chunk.choices[0].delta.content  # type: ignore
        except (AttributeError, IndexError):
            # choices can be empty for last chunk if stream_options: {"include_usage": true}
            self.content = None

    def jsonify_full_llm_response(self) -> str:
        return (
            self.chat_completion_chunk.model_dump_json()
            if self.chat_completion_chunk is not None
            else "null"
        )


class LLMTaskResponseChunk(LLMResponseChunk):
    """A chunk of an LLM task's streaming response."""

    def __init__(
        self,
        chat_completion_chunk: ChatCompletionChunk | None = None,
        event_type: TaskEventType | None = None,
        event_data: TaskEventData | None = None,
    ):
        super().__init__(chat_completion_chunk)
        self.event_type = event_type or "DEFAULT"
        self.event_data = event_data or {}

        if self.event_type == "DEFAULT" and chat_completion_chunk is None:
            raise ValueError("chat_completion_chunk is required for 'DEFAULT' event.")

    @classmethod
    def from_llm_response_chunk(
        cls,
        llm_response_chunk: LLMResponseChunk,
        event_type: TaskEventType | None = None,
        event_data: TaskEventData | None = None,
    ) -> "LLMTaskResponseChunk":
        return cls(
            chat_completion_chunk=llm_response_chunk.chat_completion_chunk,
            event_type=event_type,
            event_data=event_data,
        )

    def is_event(self) -> bool:
        """Check if this response chunk is an event, as opposed to a content chunk."""
        return self.event_type != "DEFAULT"


class GeneralTaskResponseChunk:
    """A chunk of a general task's streaming response."""

    def __init__(
        self,
        content_chunk: Any = None,
        event_type: TaskEventType | None = None,
        event_data: TaskEventData | None = None,
    ):
        self.content_chunk = content_chunk
        self.event_type = event_type or "DEFAULT"
        self.event_data = event_data or {}

    def is_event(self) -> bool:
        """Check if this response chunk is an event, as opposed to a content chunk."""
        return self.event_type != "DEFAULT"
