import time
from datetime import date, timedelta
from typing import Any, Dict, List, Sequence, Tuple

from llm.openai_client import OpenAIClient
from llm.prompt_builder import build_summary_prompt
from observability.metrics import metrics_collector
from schemas.itinerary import DayPlan
from schemas.poi import POICandidate, POISelection
from schemas.request import NormalizedRequirement
from tools.tool_factory import get_transport_tool, get_weather_tool
from utils.logger import get_logger, log_event


class ScheduleAgent:
    """根据候选 POI 和约束生成每日行程。"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.weather_tool = get_weather_tool()
        self.transport_tool = get_transport_tool()
        self.llm_client = OpenAIClient()
        self.last_weather_notes: List[str] = []
        self.last_route_notes: List[str] = []

    def _estimate_leg(
        self,
        request_id: str,
        origin: str,
        destination: str,
        mode: str,
    ) -> Dict[str, Any]:
        started = time.perf_counter()
        route = self.transport_tool.estimate_route(origin=origin, destination=destination, mode=mode)
        metrics_collector.record_tool(
            request_id=request_id,
            tool_name=self.transport_tool.name,
            duration_ms=(time.perf_counter() - started) * 1000,
        )
        metrics_collector.record_transport_fallback(
            request_id=request_id,
            triggered=bool(route.get("fallback", False)),
        )
        return route

    def _sorted_by_proximity(
        self,
        request_id: str,
        start_point: str,
        items: Sequence[POICandidate],
        mode: str,
    ) -> List[POICandidate]:
        if not items:
            return []

        remain = list(items)
        ordered: List[POICandidate] = []
        cursor = start_point
        while remain:
            scored: List[Tuple[int, float]] = []
            for idx, item in enumerate(remain):
                leg = self._estimate_leg(request_id, cursor, item.name, mode)
                scored.append((idx, float(leg["duration_min"])))
            scored.sort(key=lambda x: x[1])
            picked = remain.pop(scored[0][0])
            ordered.append(picked)
            cursor = picked.name
        return ordered

    def _pick_closest(
        self,
        base_name: str,
        items: Sequence[POICandidate],
        request_id: str,
        mode: str,
    ) -> POICandidate:
        best = items[0]
        best_min = 10**9
        for item in items:
            leg = self._estimate_leg(request_id, base_name, item.name, mode)
            if leg["duration_min"] < best_min:
                best = item
                best_min = leg["duration_min"]
        return best

    def run(self, requirement: NormalizedRequirement, poi_selection: POISelection, request_id: str) -> List[DayPlan]:
        start = time.perf_counter()

        weather_data: List[Dict[str, Any]] = []
        for i in range(requirement.days):
            target_date = (date.today() + timedelta(days=i)).isoformat()
            w_start = time.perf_counter()
            weather_info = self.weather_tool.get_weather(requirement.destination, target_date)
            metrics_collector.record_tool(
                request_id=request_id,
                tool_name=self.weather_tool.name,
                duration_ms=(time.perf_counter() - w_start) * 1000,
            )
            metrics_collector.record_weather_fallback(
                request_id=request_id,
                triggered=bool(weather_info.get("fallback", False)),
            )
            weather_data.append(weather_info)

        route_mode = "fast" if requirement.pace == "紧凑" else "economy"
        ordered_attractions = self._sorted_by_proximity(
            request_id=request_id,
            start_point=requirement.destination,
            items=poi_selection.attractions,
            mode=route_mode,
        )

        llm_hint = self.llm_client.generate(build_summary_prompt(requirement))

        plans: List[DayPlan] = []
        rainy_days = 0
        daily_commute_minutes: List[int] = []

        for i in range(requirement.days):
            attraction = ordered_attractions[i % len(ordered_attractions)]
            activity = self._pick_closest(attraction.name, poi_selection.activities, request_id, route_mode)
            food = self._pick_closest(attraction.name, poi_selection.foods, request_id, route_mode)
            weather = weather_data[i]

            leg_1 = self._estimate_leg(request_id, requirement.destination, attraction.name, route_mode)
            leg_2 = self._estimate_leg(request_id, attraction.name, activity.name, route_mode)
            leg_3 = self._estimate_leg(request_id, activity.name, food.name, route_mode)
            leg_2b = self._estimate_leg(request_id, attraction.name, food.name, route_mode)
            leg_3b = self._estimate_leg(request_id, food.name, activity.name, route_mode)

            total_af = int(leg_1["duration_min"] + leg_2["duration_min"] + leg_3["duration_min"])
            total_fa = int(leg_1["duration_min"] + leg_2b["duration_min"] + leg_3b["duration_min"])

            if total_af <= total_fa:
                order = [attraction.name, activity.name, food.name]
                route_legs = [leg_1, leg_2, leg_3]
                commute_min = total_af
            else:
                order = [attraction.name, food.name, activity.name]
                route_legs = [leg_1, leg_2b, leg_3b]
                commute_min = total_fa

            daily_commute_minutes.append(commute_min)
            total_distance = round(sum(float(leg["distance_km"]) for leg in route_legs), 1)

            if not bool(weather.get("suitable_for_outdoor", True)):
                rainy_days += 1
                morning = "上午：室内博物馆/展览"
                afternoon = "下午：室内体验活动（手作/展馆）"
            elif requirement.pace == "紧凑":
                morning = f"上午：游览 {order[0]}"
                afternoon = f"下午：{order[1]} + 周边二次探索"
            else:
                morning = f"上午：游览 {order[0]}"
                afternoon = f"下午：{order[1]}（留足休息时间）"

            weather_text = (
                f"{weather.get('condition', 'unknown')} "
                f"{weather.get('temperature_min', '-') }~{weather.get('temperature_max', '-') }℃"
            )
            transport_suggestion = (
                "步行+地铁优先，打车作为补充"
                if commute_min <= 45
                else "地铁/公交为主，跨区段可短程打车"
                if commute_min <= 90
                else "建议优先打车或网约车，减少换乘"
            )

            plans.append(
                DayPlan(
                    day=i + 1,
                    weather=weather_text,
                    activities=[
                        morning,
                        f"中午：品尝 {food.name}",
                        afternoon,
                        f"晚上：自由活动与夜间散步（{llm_hint}）",
                    ],
                    transport_tip=transport_suggestion,
                    travel_time_estimate=commute_min,
                    route_notes=f"推荐顺序：酒店 -> {order[0]} -> {order[1]} -> {order[2]}，预计总路程约{total_distance}km，总通勤约{commute_min}分钟。",
                    transport_suggestion=transport_suggestion,
                )
            )

        self.last_weather_notes = [
            f"天气建议：未来{rainy_days}天存在降雨/不适宜户外，已优先安排室内活动与美食路线。"
            if rainy_days > 0
            else "天气建议：当前天气条件适合常规户外安排。"
        ]
        self.last_route_notes = [
            f"路线优化：已按 POI 邻近度排序并尽量减少折返，日均通勤约{round(sum(daily_commute_minutes) / len(daily_commute_minutes)) if daily_commute_minutes else 0}分钟。"
        ]

        for idx, minutes in enumerate(daily_commute_minutes, start=1):
            metrics_collector.record_daily_commute(request_id=request_id, day=idx, minutes=minutes)

        duration_ms = (time.perf_counter() - start) * 1000
        log_event(
            logger=self.logger,
            request_id=request_id,
            agent_name="ScheduleAgent",
            action="build_schedule",
            duration_ms=duration_ms,
            input_summary={"days": requirement.days, "pace": requirement.pace},
            output_summary={"daily_plan_count": len(plans), "daily_commute_minutes": daily_commute_minutes},
        )
        return plans
