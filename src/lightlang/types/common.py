from openai.resources.chat.completions import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion as _ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk as _ChatCompletionChunk


# What follows is a somewhat unconventional way to export types but simply using
# __all__ is not enough to get "Quick fix" hints in the IDE.

ChatMessage = ChatCompletionMessageParam 
ChatCompletion = _ChatCompletion
ChatCompletionChunk = _ChatCompletionChunk

