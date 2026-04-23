from __future__ import annotations

import uuid
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class PlanConstraints(BaseModel):
    """用户规划约束。"""

    pace: Literal["轻松", "紧凑"] = Field(default="轻松", description="行程节奏偏好")
    indoor_first: bool = Field(default=False, description="是否优先室内活动")


class PlanRequest(BaseModel):
    """生成行程请求。"""

    origin: str = Field(..., description="出发地")
    destination: str = Field(..., description="目的地")
    days: int = Field(..., ge=1, le=14, description="旅行天数")
    budget: float = Field(..., gt=0, description="预算（人民币）")
    preferences: List[str] = Field(default_factory=list, description="偏好标签")
    constraints: PlanConstraints = Field(default_factory=PlanConstraints)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="会话 ID")
    user_id: Optional[str] = Field(default=None, description="用户 ID")


class ChatPlanRequest(BaseModel):
    user_input: str = Field(..., description="用户口语化输入")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="会话 ID")
    user_id: Optional[str] = Field(default=None, description="用户 ID")


class NormalizedRequirement(BaseModel):
    """需求解析后的标准化结构，供后续 Agent 使用。"""

    origin: str = "上海"
    destination: str = "杭州"
    days: int = 2
    budget: float = 2500
    preferences: List[str] = Field(default_factory=list)
    pace: Literal["轻松", "紧凑"] = "轻松"
    indoor_first: bool = False
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None

    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    companions: List[str] = Field(default_factory=list)
    hotel_preferences: List[str] = Field(default_factory=list)
    travel_dates: Optional[str] = None
    raw_user_input: Optional[str] = None
    clarification_needed: bool = False
    clarification_questions: List[str] = Field(default_factory=list)
    locked_constraints: Dict[str, Any] = Field(default_factory=dict)
    memory_summary: Dict[str, Any] = Field(default_factory=dict)

    extracted_preferences: Dict[str, Any] = Field(default_factory=dict)
    temporary_constraints: Dict[str, Any] = Field(default_factory=dict)
    stable_preferences: Dict[str, Any] = Field(default_factory=dict)
    override_constraints: Dict[str, Any] = Field(default_factory=dict)
    memory_applied: Dict[str, Any] = Field(default_factory=dict)
    inherited_preferences: Dict[str, Any] = Field(default_factory=dict)
    overridden_preferences: List[Dict[str, Any]] = Field(default_factory=list)


class ReplanRequest(BaseModel):
    """重规划请求。"""

    original_request: PlanRequest
    current_plan: dict

    day: int = Field(default=1, ge=1, description="兼容字段：需要重规划的天数")
    affected_days: List[int] = Field(default_factory=list, description="受影响天数列表，例如 [2]")
    locked_days: List[int] = Field(default_factory=list, description="已确认锁定日期，例如 [1]")

    reason: str = Field(..., description="重规划原因，例如 rain / poi_closed / reduce_budget")
    keep_budget: bool = Field(default=True, description="是否尽量保持预算不变")
    keep_hotel: bool = Field(default=True, description="重规划时是否保留酒店方案")
    keep_confirmed_segments: bool = Field(default=True, description="是否保留已确认片段与已锁定日期")

    new_budget: Optional[float] = Field(default=None, description="如果临时削减预算，提供新预算")
    closed_poi: Optional[str] = Field(default=None, description="关闭景点名")
    food_focus: bool = Field(default=False, description="是否加强美食安排")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="会话 ID")
    user_id: Optional[str] = Field(default=None, description="用户 ID")
