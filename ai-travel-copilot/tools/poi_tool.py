import time
from typing import Any, Dict

from observability.metrics import metrics_collector
from tools.base_tool import BaseTool
from tools.mock_poi_tool import get_poi_candidates


class POITool(BaseTool):
    name = "poi_tool"

    def run(self, destination: str, request_id: str) -> Dict[str, Any]:
        start = time.perf_counter()
        result = get_poi_candidates(destination)
        metrics_collector.record_tool(
            request_id=request_id,
            tool_name=self.name,
            duration_ms=(time.perf_counter() - start) * 1000,
        )
        return result
