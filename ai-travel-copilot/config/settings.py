from __future__ import annotations

from dataclasses import dataclass
import os


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    USE_REAL_WEATHER_API: bool = _as_bool(os.getenv("USE_REAL_WEATHER_API"), True)
    USE_REAL_POI_API: bool = _as_bool(os.getenv("USE_REAL_POI_API"), True)
    USE_REAL_HOTEL_API: bool = _as_bool(os.getenv("USE_REAL_HOTEL_API"), True)
    USE_REAL_TRANSPORT_API: bool = _as_bool(os.getenv("USE_REAL_TRANSPORT_API"), True)
    USE_REAL_SEARCH_API: bool = _as_bool(os.getenv("USE_REAL_SEARCH_API"), True)

    WEATHER_API_PROVIDER: str = os.getenv("WEATHER_API_PROVIDER", "weatherapi").strip().lower()
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "16ba00ae51d2440a9bf150229260104").strip()
    WEATHER_API_BASE_URL: str = os.getenv(
        "WEATHER_API_BASE_URL", "https://api.weatherapi.com/v1"
    ).strip()

    SEARCH_API_PROVIDER: str = os.getenv("SEARCH_API_PROVIDER", "serpapi").strip().lower()
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "e9ff0a781e16edd33849613c87151fe4006cfc36fca58d354f2e2bb81abf2736").strip()
    SEARCH_API_BASE_URL: str = os.getenv("SEARCH_API_BASE_URL", "https://serpapi.com/search.json").strip()

    LANGCHAIN_TOOL_MODE: bool = _as_bool(os.getenv("LANGCHAIN_TOOL_MODE"), False)
    LANGCHAIN_LLM_MODE: str = os.getenv("LANGCHAIN_LLM_MODE", "off").strip().lower()
    LANGCHAIN_LLM_PROVIDER: str = os.getenv("LANGCHAIN_LLM_PROVIDER", "mock").strip().lower()
    REACT_AGENT_MODE: bool = _as_bool(os.getenv("REACT_AGENT_MODE"), False)


settings = Settings()
