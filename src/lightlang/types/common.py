from typing import Any, Literal
from openai.resources.chat.completions import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion as _ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk as _ChatCompletionChunk
from pydantic import BaseModel

LLMProvider = Literal["openai", "openrouter"]

# What follows is a somewhat unconventional way to export types but simply using
# __all__ is not enough to get "Quick fix" hints in the IDE.

ChatMessage = ChatCompletionMessageParam 
ChatCompletion = _ChatCompletion
ChatCompletionChunk = _ChatCompletionChunk

# TODO: Review if should include these types in the __all__ list
TaskEventType = Literal["RESTART_TASK", "BEGIN_TASK", "END_TASK", "DEFAULT"]
TaskEventData = dict[str, Any]

class TaskStreamResult(BaseModel):
    """Result of a general task."""

    task_result: Any


class StreamResult(TaskStreamResult):
    """Result of a streaming task."""

    llm_output: str
