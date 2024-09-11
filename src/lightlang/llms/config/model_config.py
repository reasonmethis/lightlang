from typing import Any

from lightlang.llms.config.openrouter_config import OPENROUTER_MODEL_CONFIG


def _construct_default_openrouter_model_config() -> dict[str, Any]:
    return {
        model: {
            "extra_body": {
                "provider": {
                    "order": list(model_config["providers"].keys())  # type: ignore
                }
            }
        }
        for model, model_config in OPENROUTER_MODEL_CONFIG.items()
        if "providers" in model_config
    }


DEFAULT_MODEL_CONFIG_BY_PROVIDER: dict[str, Any] = {
    "openrouter": {},
    "openai": {},
}

DEFAULT_MODEL_CONFIG_BY_PROVIDER_AND_MODEL: dict[str, dict[str, Any]] = {
    "openrouter": _construct_default_openrouter_model_config(),
    "openai": {},
}
