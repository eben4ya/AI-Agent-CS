from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 0.95
DEFAULT_TOP_K = 32
DEFAULT_BACKEND_API_URL = "http://localhost:8000"


def _safe_float(value: str | None, fallback: float) -> float:
    if value is None:
        return fallback
    try:
        return float(value)
    except ValueError:
        return fallback


def _safe_int(value: str | None, fallback: int) -> int:
    if value is None:
        return fallback
    try:
        return int(value)
    except ValueError:
        return fallback


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str | None
    model: str
    temperature: float
    top_p: float
    top_k: int
    max_output_tokens: int | None


@lru_cache(maxsize=1)
def get_gemini_config() -> GeminiConfig:
    """Load Gemini configuration from environment variables."""
    return GeminiConfig(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        temperature=_safe_float(os.getenv("GEMINI_TEMPERATURE"), DEFAULT_TEMPERATURE),
        top_p=_safe_float(os.getenv("GEMINI_TOP_P"), DEFAULT_TOP_P),
        top_k=_safe_int(os.getenv("GEMINI_TOP_K"), DEFAULT_TOP_K),
        max_output_tokens=_safe_int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS"), 1024) or None,
    )


@lru_cache(maxsize=1)
def get_backend_api_base_url() -> str:
    """Base URL for calling this service's REST endpoints."""
    return os.getenv("BACKEND_API_BASE_URL", DEFAULT_BACKEND_API_URL)
