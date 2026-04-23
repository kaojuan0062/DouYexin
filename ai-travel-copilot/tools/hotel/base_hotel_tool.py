from abc import abstractmethod
from typing import Any, Dict, List, Optional

from tools.base_tool import BaseTool


class BaseHotelTool(BaseTool):
    name = "hotel_tool"

    @abstractmethod
    def search_hotels(
        self,
        city: str,
        checkin: str,
        checkout: str,
        budget_per_night: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError
