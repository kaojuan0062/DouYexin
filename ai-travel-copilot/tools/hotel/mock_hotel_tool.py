from typing import Any, Dict, List, Optional

from tools.hotel.base_hotel_tool import BaseHotelTool


class MockHotelTool(BaseHotelTool):
    def search_hotels(
        self,
        city: str,
        checkin: str,
        checkout: str,
        budget_per_night: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = [
            {
                "name": "城市精选酒店",
                "area": "市中心",
                "price_per_night": 380,
                "rating": 4.6,
                "tags": ["近地铁", "高性价比"],
            },
            {
                "name": "河畔商务酒店",
                "area": "滨江区",
                "price_per_night": 320,
                "rating": 4.4,
                "tags": ["交通便利", "安静"],
            },
            {
                "name": "青年轻居酒店",
                "area": "老城区",
                "price_per_night": 220,
                "rating": 4.2,
                "tags": ["低价", "步行友好"],
            },
        ]

        if budget_per_night is None:
            return candidates

        within_budget = [x for x in candidates if float(x["price_per_night"]) <= float(budget_per_night)]
        return within_budget or [min(candidates, key=lambda x: float(x["price_per_night"]))]
