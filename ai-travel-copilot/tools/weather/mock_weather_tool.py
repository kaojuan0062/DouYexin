from datetime import datetime
from typing import Any, Dict

from tools.weather.base_weather_tool import BaseWeatherTool


class MockWeatherTool(BaseWeatherTool):
    """Mock weather tool with deterministic responses."""

    _base = [
        {"condition": "sunny", "temperature_min": 22, "temperature_max": 28, "suitable_for_outdoor": True},
        {"condition": "cloudy", "temperature_min": 21, "temperature_max": 26, "suitable_for_outdoor": True},
        {"condition": "rain", "temperature_min": 18, "temperature_max": 24, "suitable_for_outdoor": False},
        {"condition": "partly_cloudy", "temperature_min": 20, "temperature_max": 27, "suitable_for_outdoor": True},
    ]

    def get_weather(self, city: str, date: str) -> Dict[str, Any]:
        if "rain" in date.lower():
            return {
                "city": city,
                "date": date.split("-")[0] if "-rain" in date else date,
                "condition": "rain",
                "temperature_min": 18,
                "temperature_max": 24,
                "suitable_for_outdoor": False,
                "source": "mock_weather_api",
            }

        day = datetime.strptime(date, "%Y-%m-%d").day
        picked = self._base[day % len(self._base)]
        return {
            "city": city,
            "date": date,
            "condition": picked["condition"],
            "temperature_min": picked["temperature_min"],
            "temperature_max": picked["temperature_max"],
            "suitable_for_outdoor": picked["suitable_for_outdoor"],
            "source": "mock_weather_api",
        }
