import time
from typing import Dict, List, Literal

from observability.metrics import metrics_collector
from tools.base_tool import BaseTool
from tools.mock_budget_tool import estimate_budget


class BudgetTool(BaseTool):
    name = "budget_tool"

    def run(
        self,
        total_budget: float,
        days: int,
        preferences: List[str],
        pace: Literal["轻松", "紧凑"],
        request_id: str,
    ) -> Dict:
        start = time.perf_counter()
        result = estimate_budget(
            total_budget=total_budget,
            days=days,
            preferences=preferences,
            pace=pace,
        )
        metrics_collector.record_tool(
            request_id=request_id,
            tool_name=self.name,
            duration_ms=(time.perf_counter() - start) * 1000,
        )
        return result
