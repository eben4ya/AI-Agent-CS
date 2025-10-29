from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from .config import get_gemini_config


def build_chat_model(**overrides: Any) -> ChatGoogleGenerativeAI:
    """Instantiate a Gemini chat model client configured for your environment."""
    config = get_gemini_config()
    api_key = overrides.pop("api_key", config.api_key)
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not configured. Set it in your environment before using the agent."
        )

    # Prepare keyword arguments with sensible defaults that can be overridden.
    params: dict[str, Any] = {
        "model": overrides.pop("model", config.model),
        "temperature": overrides.pop("temperature", config.temperature),
        "top_p": overrides.pop("top_p", config.top_p),
        "top_k": overrides.pop("top_k", config.top_k),
        "google_api_key": api_key,
    }

    max_tokens = overrides.pop("max_output_tokens", config.max_output_tokens)
    if max_tokens:
        params["max_output_tokens"] = max_tokens

    params.update(overrides)
    return ChatGoogleGenerativeAI(**params)


@lru_cache(maxsize=1)
def get_chat_model() -> ChatGoogleGenerativeAI:
    """Return a cached Gemini client so HTTP sessions/details are reused."""
    return build_chat_model()
