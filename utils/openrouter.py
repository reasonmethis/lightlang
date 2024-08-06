import requests
import json

OPENROUTER_BASE = "https://openrouter.ai"
OPENROUTER_API_BASE = f"{OPENROUTER_BASE}/api/v1"


def get_available_models():
    try:
        response = requests.get(f"{OPENROUTER_API_BASE}/models")
        response.raise_for_status()
        models = json.loads(response.text)["data"]
        return [model["id"] for model in models]
    except requests.exceptions.RequestException as e:
        raise e