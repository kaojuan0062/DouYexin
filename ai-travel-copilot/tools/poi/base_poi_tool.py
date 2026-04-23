from abc import abstractmethod
from typing import Any, Dict, List

from tools.base_tool import BaseTool


class BasePOITool(BaseTool):
    name = "poi_tool"

    @abstractmethod
    def search_pois(self, city: str, preferences: List[str]) -> Dict[str, Any]:
        raise NotImplementedError
