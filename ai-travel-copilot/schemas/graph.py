from typing import Any, Dict, List, Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class DayPlan(BaseModel):
    day: int
    weather: str
    activities: List[str]
    transport_tip: str
    travel_time_estimate: int = 0
    route_notes: str = ""
    transport_suggestion: str = ""


class GraphTravelRequest(BaseModel):
    mode: Literal["generate", "replan"] = "generate"
    user_input: str = Field(default="", description="自然语言输入，generate 模式使用")
    session_id: str = Field(..., description="会话 ID")
    user_id: Optional[str] = Field(default=None, description="用户 ID")
    original_request: Optional[Dict[str, Any]] = Field(default=None, description="可选结构化原始请求")
    current_plan: Dict[str, Any] = Field(default_factory=dict, description="replan 模式下当前计划")
    reason: str = Field(default="rain", description="replan 原因")
    affected_days: List[int] = Field(default_factory=list)
    locked_days: List[int] = Field(default_factory=list)
    keep_budget: bool = True
    keep_hotel: bool = True
    keep_confirmed_segments: bool = True
    new_budget: Optional[float] = None
    closed_poi: Optional[str] = None
    food_focus: bool = False


class GraphTravelResponse(BaseModel):
    mode: str
    state: Dict[str, Any]
    itinerary: Dict[str, Any] = Field(default_factory=dict)


class TravelState(TypedDict, total=False):
    mode: str
    request_id: str
    session_id: str
    user_id: Optional[str]
    user_input: str
    original_request: Dict[str, Any]
    current_plan: Dict[str, Any]
    reason: str
    affected_days: List[int]
    locked_days: List[int]
    keep_budget: bool
    keep_hotel: bool
    keep_confirmed_segments: bool
    new_budget: Optional[float]
    closed_poi: Optional[str]
    food_focus: bool
    memory_context: Dict[str, Any]
    normalized_requirement: Dict[str, Any]
    rewritten_queries: Dict[str, List[str]]
    research_results: Dict[str, Any]
    candidate_pool: Dict[str, List[Dict[str, Any]]]
    recommendation_reasons: List[str]
    candidate_pool_summary: Dict[str, Any]
    itinerary: Dict[str, Any]
    react_trace: List[Dict[str, str]]
