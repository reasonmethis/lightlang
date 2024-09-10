from openai.resources.chat.completions import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion as _ChatCompletion

# Export necessary types
ChatMessage = ChatCompletionMessageParam
ChatCompletion = _ChatCompletion
