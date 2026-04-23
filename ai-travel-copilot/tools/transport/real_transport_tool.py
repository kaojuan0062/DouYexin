import time
from hashlib import md5
from typing import Any, Dict

from tools.transport.base_transport_tool import BaseTransportTool


class RealTransportTool(BaseTransportTool):
    """模拟真实地图 API（可按环境变量切换为真实实现）。"""

    _MODE_SPEED_KMH = {
        "walk": 5.0,
        "metro": 30.0,
        "bus": 22.0,
        "taxi": 35.0,
        "economy": 25.0,
        "fast": 40.0,
    }

    def _simulated_external_call(self, origin: str, destination: str) -> float:
        """模拟外部 API 返回的距离。"""
        seed = md5(f"real::{origin}->{destination}".encode("utf-8")).hexdigest()
        raw = int(seed[:8], 16)
        return round(1.5 + (raw % 6200) / 100.0, 1)  # 1.5~63.5km

    def estimate_route(
        self,
        origin: str,
        destination: str,
        mode: str = "taxi",
    ) -> Dict[str, Any]:
        started = time.perf_counter()
        distance_km = self._simulated_external_call(origin=origin, destination=destination)
        speed_kmh = self._MODE_SPEED_KMH.get(mode, self._MODE_SPEED_KMH["taxi"])
        duration_min = max(6, round(distance_km / speed_kmh * 60 + 5))

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
            "source": "real_transport_api",
            "api_duration_ms": round((time.perf_counter() - started) * 1000, 2),
        }
