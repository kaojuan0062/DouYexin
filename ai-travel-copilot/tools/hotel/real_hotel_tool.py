from hashlib import md5
from typing import Any, Dict, List, Optional

from tools.hotel.base_hotel_tool import BaseHotelTool


class RealHotelTool(BaseHotelTool):
    """模拟真实酒店 API（可按环境变量切换为真实实现）。"""

    def _price(self, city: str, idx: int) -> int:
        seed = md5(f"{city}-{idx}".encode("utf-8")).hexdigest()
        raw = int(seed[:8], 16)
        return 200 + raw % 280

    def search_hotels(
        self,
        city: str,
        checkin: str,
        checkout: str,
        budget_per_night: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        hotels: List[Dict[str, Any]] = [
            {
                "name": f"{city}智选酒店A",
                "area": "市中心",
                "price_per_night": self._price(city, 1),
                "rating": 4.5,
                "tags": ["近地铁", "商务"],
            },
            {
                "name": f"{city}智选酒店B",
                "area": "景区周边",
                "price_per_night": self._price(city, 2),
                "rating": 4.3,
                "tags": ["景区便利", "亲子"],
            },
            {
                "name": f"{city}轻居酒店C",
                "area": "老城区",
                "price_per_night": self._price(city, 3),
                "rating": 4.1,
                "tags": ["低价", "本地生活圈"],
            },
        ]

        if budget_per_night is None:
            return hotels

        within_budget = [x for x in hotels if float(x["price_per_night"]) <= float(budget_per_night)]
        return within_budget or [min(hotels, key=lambda x: float(x["price_per_night"]))]
