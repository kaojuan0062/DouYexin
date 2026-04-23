from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from schemas.budget import BudgetBreakdown, HotelRecommendation


class DayPlan(BaseModel):
    """单日行程。"""

    day: int
    weather: str
    activities: List[str]
    transport_tip: str
    travel_time_estimate: int = 0
    route_notes: str = ""
    transport_suggestion: str = ""


class ItineraryResponse(BaseModel):
    """最终行程输出。"""

    summary: str
    daily_plan: List[DayPlan]
    estimated_budget: BudgetBreakdown
    notes: List[str]

    hotel_recommendations: List[HotelRecommendation] = Field(default_factory=list)
    budget_breakdown: Dict[str, float] = Field(default_factory=dict)
    over_budget_flag: bool = False
    optimization_suggestions: List[str] = Field(default_factory=list)

    planning_trace_summary: Dict[str, object] = Field(default_factory=dict)
    tool_usage_summary: Dict[str, object] = Field(default_factory=dict)
    replanning_diff: Optional[Dict[str, object]] = None

    normalized_requirements: Dict[str, object] = Field(default_factory=dict)
    query_rewrites: Dict[str, List[str]] = Field(default_factory=dict)
    source_summary: Dict[str, object] = Field(default_factory=dict)
    recommendation_reasons: List[str] = Field(default_factory=list)
    candidate_pool_summary: Dict[str, object] = Field(default_factory=dict)
    reused_memory_summary: Dict[str, Any] = Field(default_factory=dict)
    preserved_constraints: Dict[str, Any] = Field(default_factory=dict)

    research_memory_hit: bool = False
    reused_candidates_count: int = 0
    refreshed_queries: Dict[str, List[str]] = Field(default_factory=dict)
    cache_strategy: str = "full_refresh"

    meta: Dict = Field(default_factory=dict)


class ChatPlanResponse(BaseModel):
    normalized_requirements: Dict[str, object]
    rewritten_queries: Dict[str, List[str]]
    research_summary: Dict[str, object]
    recommended_candidates: Dict[str, List[Dict[str, object]]]
    memory_applied: Dict[str, Any] = Field(default_factory=dict)
    inherited_preferences: Dict[str, Any] = Field(default_factory=dict)
    overridden_preferences: List[Dict[str, Any]] = Field(default_factory=list)
    research_memory_hit: bool = False
    reused_candidates_count: int = 0
    refreshed_queries: Dict[str, List[str]] = Field(default_factory=dict)
    cache_strategy: str = "full_refresh"
    final_plan: ItineraryResponse
