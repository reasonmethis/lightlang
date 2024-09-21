from typing import Any


DEFAULT_PROVIDER_CONFIGS: dict[str, dict[str, Any]] = {
    "openai": {
        "api_type": "openai",
        "base_url": None,  # will default to "https://api.openai.com/v1"
        "api_key_env_var": "OPENAI_API_KEY",
    },
    "openrouter": {
        "api_type": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env_var": "OPENROUTER_API_KEY",
    },
}

ALLOWED_LLM_PROVIDERS = tuple(DEFAULT_PROVIDER_CONFIGS.keys())
