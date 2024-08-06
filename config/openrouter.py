MODELS = {
    "meta-llama/llama-3-70b-instruct": {
        "context": 8192,
        "providers": {
            "DeepInfra": {"input": 0.59, "output": 0.79, "latency": 0.45},
        },
    },
    "mistralai/mixtral-8x7b-instruct": {
        "context": 32768,
        "providers": {
            "DeepInfra": {"input": 0.24, "output": 0.24, "latency": 0.55},
        },
    },
    "mistralai/mistral-7b-instruct:nitro": {
        "context": 32768,
        "providers": {
            "Lepton": {"input": 0.11, "output": 0.11, "latency": 0.73},
            "Fireworks": {"input": 0.2, "output": 0.2, "latency": 0.13},
        },
    },
    "microsoft/wizardlm-2-8x22b": {
        "context": 65536,
        "providers": {
            "DeepInfra": {
                "input": 0.65,
                "output": 0.65,
                "latency": 0.58,
                "max_output": 65536,
            },
            "NovitaAI": {
                "input": 0.64,
                "output": 0.64,
                "latency": 2.14,
                "max_output": 65536,
            },
        },
    },
    "openai/gpt-3.5-turbo-0125": {
        "context": 16385,
        "providers": {
            "OpenAI": {"input": 0.5, "output": 1.5, "latency": 0.63},
        },
    },
    "openai/gpt-4-turbo": {
        "context": 128000,
        "providers": {
            "OpenAI": {"input": 10, "output": 30, "latency": 1.34},
        },
    },
    "openai/gpt-4o": {
        "context": 128000,
        "providers": {
            "OpenAI": {"input": 5, "output": 15, "max_output": 4096, "latency": 0.74},
        },
    },
    "openai/gpt-4o-mini": {
        "context": 128000,
        "providers": {
            "OpenAI": {
                "input": 0.15,
                "output": 0.6,
                "input_img": 7.225,
                "max_output": 16384,
                "latency": 0.54,
                "tps": 73.3,
            },
        },
    },
    "anthropic/claude-3.5-sonnet": {
        "context": 200000,
        "providers": {
            "Anthropic": {"input": 3, "output": 15, "latency": 1.8, "max_output": 4096},
        },
    },
    "google/gemini-pro-1.5": {
        "context": 2800000,
        "providers": {
            "Google": {
                "input": 2.5,
                "output": 7.5,
                "max_output": 22937,
                "latency": 1.42,
                "tps": 59.94,
            },
        },
    },
    "meta-llama/llama-3-8b-instruct:free": {"context": 8192},
    "mistralai/mistral-7b-instruct:free": {"context": 32768},
}

DEFAULT_FREE_MODEL = "meta-llama/llama-3-8b-instruct:free"
DEFAULT_CHEAP_MODEL = "openai/gpt-4o-mini"
DEFAULT_SMART_MODEL = "openai/gpt-4o"

MODEL_ALIASES = {
    "DEFAULT_FREE_MODEL": DEFAULT_FREE_MODEL,
    "DEFAULT_CHEAP_MODEL": DEFAULT_CHEAP_MODEL,
    "DEFAULT_SMART_MODEL": DEFAULT_SMART_MODEL,
}