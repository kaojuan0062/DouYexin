from abc import ABC, abstractmethod
from typing import Dict, List

SearchResult = Dict[str, str]


class BaseSearchTool(ABC):
    name = "search_tool"

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        raise NotImplementedError
