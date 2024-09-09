from lightlang.models import ChatMessage


def get_user_message(message: str) -> ChatMessage:
    return {"role": "user", "content": message}


def get_system_message(message: str) -> ChatMessage:
    return {"role": "system", "content": message}


def get_assistant_message(message: str) -> ChatMessage:
    return {"role": "assistant", "content": message}
