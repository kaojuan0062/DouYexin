from typing import List

import requests

from config.settings import settings
from tools.search.base_search_tool import BaseSearchTool, SearchResult


class RealSearchTool(BaseSearchTool):
    name = "search_tool"

    def __init__(self) -> None:
        self.api_key = settings.SEARCH_API_KEY
        self.base_url = settings.SEARCH_API_BASE_URL

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        if not self.api_key:
            raise ValueError("SEARCH_API_KEY is required for real search")

        resp = requests.get(
            self.base_url,
            params={"q": query, "api_key": self.api_key, "num": top_k},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()

        organic = data.get("organic_results", [])[:top_k]
        results: List[SearchResult] = []
        for item in organic:
            results.append(
                {
                    "title": str(item.get("title", "")),
                    "snippet": str(item.get("snippet", "")),
                    "source": str(item.get("source", "serpapi")),
                    "url": str(item.get("link", "")),
                    "category": "general",
                }
            )
        return results
