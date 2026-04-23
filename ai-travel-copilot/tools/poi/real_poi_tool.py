from typing import Any, Dict, List

from tools.poi.base_poi_tool import BasePOITool


class RealPOITool(BasePOITool):
    """Placeholder for future real POI API integration."""

    def search_pois(self, city: str, preferences: List[str]) -> Dict[str, Any]:
        raise NotImplementedError(
            "RealPOITool is not implemented yet. "
            "Set USE_REAL_POI_API=false to use mock mode."
        )
