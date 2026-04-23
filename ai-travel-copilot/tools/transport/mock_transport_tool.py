from hashlib import md5
from typing import Any, Dict

from tools.transport.base_transport_tool import BaseTransportTool


class MockTransportTool(BaseTransportTool):
    _MODE_SPEED_KMH = {
        "walk": 4.5,
        "metro": 28.0,
        "bus": 20.0,
        "taxi": 32.0,
        "economy": 24.0,
        "fast": 36.0,
    }

    def _pseudo_distance_km(self, origin: str, destination: str) -> float:
        seed = md5(f"{origin}->{destination}".encode("utf-8")).hexdigest()
        raw = int(seed[:8], 16)
        return round(2.0 + (raw % 4800) / 100.0, 1)  # 2.0~50.0km

    def estimate_route(
        self,
        origin: str,
        destination: str,
        mode: str = "taxi",
    ) -> Dict[str, Any]:
        distance_km = self._pseudo_distance_km(origin, destination)
        speed_kmh = self._MODE_SPEED_KMH.get(mode, self._MODE_SPEED_KMH["taxi"])
        duration_min = max(8, round(distance_km / speed_kmh * 60 + 6))

        normalized_mode = {
            "fast": "taxi",
            "economy": "metro",
        }.get(mode, mode)

        return {
            "origin": origin,
            "destination": destination,
            "distance_km": distance_km,
            "duration_min": duration_min,
            "mode": normalized_mode,
            "source": "mock_transport_api",
        }
