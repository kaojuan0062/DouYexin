from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class HotelRecommendation(BaseModel):
    name: str
    area: str
    price_per_night: float
    rating: float
    tags: List[str] = Field(default_factory=list)


class BudgetBreakdown(BaseModel):
    """预算拆分结果。"""

    total: float
    by_category: Dict[str, float]
    daily_average: float
    within_budget: bool
    warning: Optional[str] = None
    preference_tags: List[str]

    hotel_recommendations: List[HotelRecommendation] = Field(default_factory=list)
    budget_breakdown: Dict[str, float] = Field(default_factory=dict)
    over_budget_flag: bool = False
    optimization_suggestions: List[str] = Field(default_factory=list)
