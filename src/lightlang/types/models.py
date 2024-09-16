from typing import Any

from pydantic import BaseModel

from lightlang.types.common import ChatCompletion, ChatCompletionChunk, TaskEvent


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

    def __init__(self, chat_completion_chunk: ChatCompletionChunk | None = None):
        self.chat_completion_chunk = chat_completion_chunk

        try:
            self.content = self.chat_completion_chunk.choices[0].delta.content  # type: ignore
        except (AttributeError, IndexError):
            # choices can be empty for last chunk if stream_options: {"include_usage": true}
            self.content = None

    def to_json(self) -> str:
        return (
            self.chat_completion_chunk.model_dump_json()
            if self.chat_completion_chunk is not None
            else ""
        )


class LLMTaskResponseChunk(LLMResponseChunk):
    """A chunk of an LLM task's streaming response."""

    def __init__(
        self,
        chat_completion_chunk: ChatCompletionChunk | None = None,
        task_event: TaskEvent | None = None,
    ):
        super().__init__(chat_completion_chunk)

        # If no task_event is provided, create and assign a default one
        if task_event is None:
            if chat_completion_chunk is None:
                raise ValueError("No chat_completion_chunk or task_event provided.")
            task_event = TaskEvent(event="UPDATE_TASK")
        self.task_event = task_event
    
    @classmethod
    def from_llm_response_chunk(
        cls, llm_response_chunk: LLMResponseChunk, task_event: TaskEvent | None = None
    ) -> "LLMTaskResponseChunk":
        return cls(
            chat_completion_chunk=llm_response_chunk.chat_completion_chunk,
            task_event=task_event,
        )


class GeneralTaskResponseChunk:
    """A chunk of a general task's streaming response."""

    def __init__(self, content_chunk: Any = None, task_event: TaskEvent | None = None):
        self.content_chunk = content_chunk
        self.task_event = task_event
