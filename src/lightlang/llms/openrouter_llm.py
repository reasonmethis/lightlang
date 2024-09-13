import httpx

OPENROUTER_BASE = "https://openrouter.ai"
OPENROUTER_API_BASE = f"{OPENROUTER_BASE}/api/v1"


def get_available_models():
    try:
        response = httpx.get(f"{OPENROUTER_API_BASE}/models")
        response.raise_for_status()
        models = response.json()["data"]
        return [model["id"] for model in models]
    except httpx.RequestError as e:
        raise e


if __name__ == "__main__":
    print(get_available_models())
