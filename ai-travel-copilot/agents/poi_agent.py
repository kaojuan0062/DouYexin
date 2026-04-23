import time
from datetime import date
from typing import Dict, List, Optional

from observability.metrics import metrics_collector
from schemas.poi import POICandidate, POISelection
from schemas.request import NormalizedRequirement
from tools.tool_factory import get_poi_tool, get_weather_tool
from utils.logger import get_logger, log_event


class POIAgent:
    """负责筛选景点/餐饮/活动候选。"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.poi_tool = get_poi_tool()
        self.weather_tool = get_weather_tool()

    def _from_web_items(self, items: List[Dict[str, object]], category: str) -> List[POICandidate]:
        result: List[POICandidate] = []
        for item in items:
            name = str(item.get("title") or item.get("name") or "")
            snippet = str(item.get("snippet", ""))
            if not name:
                continue
            result.append(
                POICandidate(
                    name=name,
                    category=category,
                    indoor=("室内" in snippet),
                    tags=["web", "fused"],
                )
            )
        return result

    def run(
        self,
        requirement: NormalizedRequirement,
        request_id: str,
        fused_candidates: Optional[Dict[str, List[Dict[str, object]]]] = None,
    ) -> POISelection:
        start = time.perf_counter()

        p_start = time.perf_counter()
        raw = self.poi_tool.search_pois(
            city=requirement.destination,
            preferences=requirement.preferences,
        )
        metrics_collector.record_tool(
            request_id=request_id,
            tool_name=self.poi_tool.name,
            duration_ms=(time.perf_counter() - p_start) * 1000,
        )

        w_start = time.perf_counter()
        weather_hint = self.weather_tool.get_weather(requirement.destination, date.today().isoformat())
        metrics_collector.record_tool(
            request_id=request_id,
            tool_name=self.weather_tool.name,
            duration_ms=(time.perf_counter() - w_start) * 1000,
        )
        metrics_collector.record_weather_fallback(
            request_id=request_id,
            triggered=bool(weather_hint.get("fallback", False)),
        )

        attractions = [POICandidate(**item) for item in raw["attractions"]]
        foods = [POICandidate(**item) for item in raw["foods"]]
        activities = [POICandidate(**item) for item in raw["activities"]]

        if fused_candidates:
            attractions = self._from_web_items(fused_candidates.get("poi", []), "attraction") + attractions
            foods = self._from_web_items(fused_candidates.get("food", []), "food") + foods
            activities = self._from_web_items(fused_candidates.get("fallback", []), "activity") + activities

        weather_indoor_bias = not bool(weather_hint.get("suitable_for_outdoor", True))
        if requirement.indoor_first or weather_indoor_bias:
            indoor_attractions = [x for x in attractions if x.indoor]
            indoor_activities = [x for x in activities if x.indoor]
            attractions = indoor_attractions or attractions
            activities = indoor_activities or activities

        result = POISelection(
            attractions=attractions,
            foods=foods,
            activities=activities,
        )

        duration_ms = (time.perf_counter() - start) * 1000
        log_event(
            logger=self.logger,
            request_id=request_id,
            agent_name="POIAgent",
            action="select_candidates",
            duration_ms=duration_ms,
            input_summary={
                "destination": requirement.destination,
                "indoor_first": requirement.indoor_first,
                "weather_outdoor_ok": bool(weather_hint.get("suitable_for_outdoor", True)),
            },
            output_summary={
                "attractions": len(result.attractions),
                "foods": len(result.foods),
                "activities": len(result.activities),
            },
        )
        return result
