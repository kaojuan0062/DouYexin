from typing import List

from pydantic import BaseModel


class POICandidate(BaseModel):
    """候选 POI/餐饮/活动。"""

    name: str
    category: str
    indoor: bool
    tags: List[str]


class POISelection(BaseModel):
    """POI Agent 的筛选结果。"""

    attractions: List[POICandidate]
    foods: List[POICandidate]
    activities: List[POICandidate]
