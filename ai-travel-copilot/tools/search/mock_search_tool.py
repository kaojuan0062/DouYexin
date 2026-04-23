from typing import List

from tools.search.base_search_tool import BaseSearchTool, SearchResult


class MockSearchTool(BaseSearchTool):
    name = "search_tool"

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        samples = [
            {
                "title": "西湖断桥日落机位攻略",
                "snippet": "西湖傍晚拍照好看，情侣出片率高，地铁1号线可达。",
                "source": "MockTravel",
                "url": "https://mock.local/hz-westlake",
                "category": "poi",
            },
            {
                "title": "杭州本地小馆榜单",
                "snippet": "推荐葱包烩、片儿川、定胜糕，人均60-100。",
                "source": "MockFood",
                "url": "https://mock.local/hz-food",
                "category": "food",
            },
            {
                "title": "武林广场地铁口高性价比酒店",
                "snippet": "地铁方便，情侣出行友好，价格300-450/晚。",
                "source": "MockStay",
                "url": "https://mock.local/hz-hotel",
                "category": "hotel",
            },
            {
                "title": "杭州雨天室内约会去处",
                "snippet": "美术馆、茶文化馆、室内展览等。",
                "source": "MockGuide",
                "url": "https://mock.local/hz-rain",
                "category": "fallback",
            },
        ]
        return samples[:top_k]
