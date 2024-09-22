# from lightlang.types.common import ChatUserMessage, ChatSystemMessage, ChatAssistantMessage


def get_user_message(message: str): # -> ChatUserMessage: # incompatible with dict[str, Any]
    return {"role": "user", "content": message}


def get_system_message(message: str): # -> ChatSystemMessage:
    return {"role": "system", "content": message}


def get_assistant_message(message: str): #-> ChatAssistantMessage:
    return {"role": "assistant", "content": message}
