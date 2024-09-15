from typing import TypeGuard

from lightlang.llms.config.provider_config import ALLOWED_LLM_PROVIDERS
from lightlang.types.common import LLMProvider


def is_allowed_llm_provider(provider: str) -> TypeGuard[LLMProvider]:
    return provider in ALLOWED_LLM_PROVIDERS
