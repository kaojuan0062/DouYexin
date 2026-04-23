from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import requests

from config.settings import settings
from tools.weather.base_weather_tool import BaseWeatherTool


class RealWeatherTool(BaseWeatherTool):
    """Real weather tool using external weather API."""

    def __init__(self) -> None:
        self.provider = settings.WEATHER_API_PROVIDER
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_BASE_URL

    def get_weather(self, city: str, date: str) -> Dict[str, Any]:
        clean_date = date.split("-rain")[0]
        if not self.api_key:
            raise RuntimeError("WEATHER_API_KEY is missing for real weather API.")

        if self.provider != "weatherapi":
            raise RuntimeError(
                f"Unsupported WEATHER_API_PROVIDER={self.provider}. "
                "Currently only 'weatherapi' is implemented."
            )

        endpoint = f"{self.base_url.rstrip('/')}/forecast.json"
        params = {
            "key": self.api_key,
            "q": city,
            "dt": clean_date,
            "days": 1,
            "aqi": "no",
            "alerts": "no",
        }

        try:
            response = requests.get(endpoint, params=params, timeout=6)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Weather API request failed: {exc}") from exc

        forecast_days = data.get("forecast", {}).get("forecastday", [])
        if not forecast_days:
            raise RuntimeError("Weather API returned empty forecast result.")

        day_info = forecast_days[0].get("day", {})
        condition_text = day_info.get("condition", {}).get("text", "unknown")
        normalized_condition = self._normalize_condition(condition_text)
        temp_min = day_info.get("mintemp_c")
        temp_max = day_info.get("maxtemp_c")

        if temp_min is None or temp_max is None:
            raise RuntimeError("Weather API missing temperature fields.")

        suitable_for_outdoor = normalized_condition not in {"rain", "storm", "snow"}
        return {
            "city": data.get("location", {}).get("name", city),
            "date": clean_date,
            "condition": normalized_condition,
            "temperature_min": round(float(temp_min)),
            "temperature_max": round(float(temp_max)),
            "suitable_for_outdoor": suitable_for_outdoor,
            "source": "real_weather_api",
        }

    def _normalize_condition(self, text: str) -> str:
        lowered = text.lower()
        if "rain" in lowered or "drizzle" in lowered:
            return "rain"
        if "snow" in lowered or "sleet" in lowered:
            return "snow"
        if "storm" in lowered or "thunder" in lowered:
            return "storm"
        if "cloud" in lowered or "overcast" in lowered:
            return "cloudy"
        if "sun" in lowered or "clear" in lowered:
            return "sunny"
        return "unknown"
