import time
from typing import List

from observability.metrics import metrics_collector
from tools.base_tool import BaseTool
from tools.mock_weather_tool import get_weather_for_day, get_weather_forecast


class WeatherTool(BaseTool):
    name = "weather_tool"

    def run(self, destination: str, days: int, request_id: str) -> List[str]:
        start = time.perf_counter()
        result = get_weather_forecast(destination, days)
        metrics_collector.record_tool(
            request_id=request_id,
            tool_name=self.name,
            duration_ms=(time.perf_counter() - start) * 1000,
        )
        return result

    def run_for_day(self, destination: str, day: int, reason: str, request_id: str) -> str:
        start = time.perf_counter()
        result = get_weather_for_day(destination=destination, day=day, reason=reason)
        metrics_collector.record_tool(
            request_id=request_id,
            tool_name=self.name,
            duration_ms=(time.perf_counter() - start) * 1000,
        )
        return result
