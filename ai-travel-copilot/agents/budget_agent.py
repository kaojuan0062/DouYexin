import time
from datetime import date, timedelta
from typing import List

from observability.metrics import metrics_collector
from schemas.budget import BudgetBreakdown, HotelRecommendation
from schemas.request import NormalizedRequirement
from tools.tool_factory import get_hotel_tool
from utils.logger import get_logger, log_event


class BudgetAgent:
    """预算估算与约束检查（含酒店搜索与超预算优化）。"""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.hotel_tool = get_hotel_tool()

    def _nights(self, days: int) -> int:
        return max(1, days - 1)

    def run(self, requirement: NormalizedRequirement, request_id: str) -> BudgetBreakdown:
        start = time.perf_counter()

        nights = self._nights(requirement.days)
        checkin = date.today().isoformat()
        checkout = (date.today() + timedelta(days=nights)).isoformat()
        target_hotel_budget = max(120.0, requirement.budget * 0.35 / nights)

        h_start = time.perf_counter()
        hotels_raw = self.hotel_tool.search_hotels(
            city=requirement.destination,
            checkin=checkin,
            checkout=checkout,
            budget_per_night=target_hotel_budget,
        )
        metrics_collector.record_tool(
            request_id=request_id,
            tool_name=self.hotel_tool.name,
            duration_ms=(time.perf_counter() - h_start) * 1000,
        )
        metrics_collector.record_hotel_fallback(
            request_id=request_id,
            triggered=any(bool(x.get("fallback", False)) for x in hotels_raw),
        )

        hotels = [HotelRecommendation(**x) for x in hotels_raw]
        selected = min(hotels, key=lambda x: x.price_per_night)
        hotel_cost = round(selected.price_per_night * nights, 2)

        pace_food_ratio = 0.27 if requirement.pace == "紧凑" else 0.23
        transport_ratio = 0.18 if requirement.pace == "紧凑" else 0.15

        food_cost = round(requirement.budget * pace_food_ratio, 2)
        tickets_cost = round(requirement.budget * 0.12, 2)
        city_transport_cost = round(requirement.budget * transport_ratio, 2)

        total_estimated = round(hotel_cost + food_cost + tickets_cost + city_transport_cost, 2)
        misc = round(requirement.budget - total_estimated, 2)

        over_budget_flag = total_estimated > requirement.budget
        optimization_suggestions: List[str] = []

        if over_budget_flag:
            selected = min(hotels, key=lambda x: x.price_per_night)
            hotel_cost = round(selected.price_per_night * nights, 2)

            tickets_cost = round(tickets_cost * 0.75, 2)
            food_cost = round(food_cost * 0.9, 2)

            total_estimated = round(hotel_cost + food_cost + tickets_cost + city_transport_cost, 2)
            misc = round(requirement.budget - total_estimated, 2)
            over_budget_flag = total_estimated > requirement.budget

            optimization_suggestions.extend(
                [
                    "已切换为更低价酒店以控制住宿成本。",
                    "已压缩高消费活动（门票/付费体验）。",
                    "餐饮建议增加本地平价餐馆占比。",
                ]
            )

        warning = None
        if over_budget_flag:
            warning = "预算仍偏紧：建议缩短天数或提高总预算。"
            optimization_suggestions.append("可考虑减少1天行程，优先保留核心景点。")

        by_category = {
            "hotel": hotel_cost,
            "food": food_cost,
            "tickets": tickets_cost,
            "transport": city_transport_cost,
            "misc": misc,
        }

        result = BudgetBreakdown(
            total=round(total_estimated, 2),
            by_category=by_category,
            daily_average=round(total_estimated / requirement.days, 2),
            within_budget=not over_budget_flag,
            warning=warning,
            preference_tags=requirement.preferences,
            hotel_recommendations=sorted(hotels, key=lambda x: x.price_per_night),
            budget_breakdown=by_category,
            over_budget_flag=over_budget_flag,
            optimization_suggestions=optimization_suggestions,
        )

        duration_ms = (time.perf_counter() - start) * 1000
        log_event(
            logger=self.logger,
            request_id=request_id,
            agent_name="BudgetAgent",
            action="estimate_budget",
            duration_ms=duration_ms,
            input_summary={"budget": requirement.budget, "days": requirement.days},
            output_summary={
                "within_budget": result.within_budget,
                "over_budget_flag": result.over_budget_flag,
                "selected_hotel": selected.name,
                "hotel_cost": hotel_cost,
            },
        )
        return result
