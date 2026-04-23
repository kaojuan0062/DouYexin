"""向后兼容聚合入口：保留第一轮 imports 可用。"""

from schemas.itinerary import DayPlan, ItineraryResponse
from schemas.request import PlanRequest, ReplanRequest

# 兼容第一轮命名
PlanResponse = ItineraryResponse

__all__ = [
    "PlanRequest",
    "ReplanRequest",
    "DayPlan",
    "ItineraryResponse",
    "PlanResponse",
]
