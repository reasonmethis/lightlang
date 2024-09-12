import os

DEFAULT_PROVIDER_CONFIGS = {
    "openai": {
        "api_type": "openai",
        "base_url": None, # will default to "https://api.openai.com/v1"
        "api_key": os.getenv("OPENAI_API_KEY"),  # TODO: Deal with if this is None
    },
    "openrouter": {
        "api_type": "openai",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_API_KEY"),
    },
}
