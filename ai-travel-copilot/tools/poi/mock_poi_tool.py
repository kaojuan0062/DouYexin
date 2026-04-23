from typing import Any, Dict, List

from tools.poi.base_poi_tool import BasePOITool


class MockPOITool(BasePOITool):
    def search_pois(self, city: str, preferences: List[str]) -> Dict[str, Any]:
        return {
            "destination": city,
            "attractions": [
                {"name": "城市博物馆", "category": "attraction", "indoor": True, "tags": ["历史", "亲子"]},
                {"name": "滨江公园", "category": "attraction", "indoor": False, "tags": ["夜景", "休闲"]},
                {"name": "历史文化街区", "category": "attraction", "indoor": False, "tags": ["历史", "美食"]},
                {"name": "艺术中心", "category": "attraction", "indoor": True, "tags": ["艺术", "轻松"]},
            ],
            "foods": [
                {"name": "本地特色小吃", "category": "food", "indoor": True, "tags": ["美食"]},
                {"name": "网红餐厅", "category": "food", "indoor": True, "tags": ["美食", "夜景"]},
                {"name": "老字号面馆", "category": "food", "indoor": True, "tags": ["历史", "美食"]},
            ],
            "activities": [
                {"name": "城市漫步", "category": "activity", "indoor": False, "tags": ["轻松", "拍照"]},
                {"name": "展馆深度游", "category": "activity", "indoor": True, "tags": ["历史", "亲子"]},
                {"name": "夜景打卡", "category": "activity", "indoor": False, "tags": ["夜景"]},
            ],
        }
