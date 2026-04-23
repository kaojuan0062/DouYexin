import json

from llm.base_client import BaseLLMClient


class MockLLMClient(BaseLLMClient):
    """Deterministic local mock client."""

    def generate(self, prompt: str) -> str:
        if "检索查询重写助手" in prompt:
            return json.dumps(
                {
                    "poi_queries": ["杭州 必去 景点", "杭州 两日游 景点"],
                    "food_queries": ["杭州 本地特色 美食", "杭州 小吃 推荐"],
                    "hotel_queries": ["杭州 地铁方便 酒店", "杭州 高性价比 酒店"],
                    "fallback_queries": ["杭州 旅游 攻略", "杭州 周末 行程"],
                },
                ensure_ascii=False,
            )
        if "旅行需求解析器" in prompt:
            return json.dumps(
                {
                    "origin": "当前城市",
                    "destination": "杭州",
                    "days": 2,
                    "budget": 2500,
                    "budget_min": 2000,
                    "budget_max": 3000,
                    "companions": ["朋友"],
                    "preferences": ["美食"],
                    "pace": "轻松",
                    "indoor_first": False,
                    "hotel_preferences": ["地铁方便"],
                    "travel_dates": None,
                    "clarification_needed": False,
                    "clarification_questions": [],
                    "stable_preferences": {
                        "preferences": ["美食"],
                        "hotel_preferences": ["地铁方便"],
                        "pace": "轻松",
                        "indoor_first": False,
                    },
                    "temporary_constraints": {
                        "days": 2,
                        "budget": 2500,
                        "budget_min": 2000,
                        "budget_max": 3000,
                    },
                    "override_constraints": {
                        "avoid_preferences": [],
                        "avoid_pois": [],
                        "avoid_categories": [],
                    },
                },
                ensure_ascii=False,
            )
        if "紧凑" in prompt:
            return "已按紧凑节奏生成高密度行程建议。"
        return "已按轻松节奏生成舒适型行程建议。"

    def generate_json(self, prompt: str):
        return json.loads(self.generate(prompt))
