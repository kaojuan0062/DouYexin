from abc import abstractmethod
from typing import Any, Dict

from tools.base_tool import BaseTool


class BaseWeatherTool(BaseTool):
    name = "weather_tool"

    @abstractmethod
    def get_weather(self, city: str, date: str) -> Dict[str, Any]:
        raise NotImplementedError
