import time

from config.settings import settings
from tools.hotel.base_hotel_tool import BaseHotelTool
from tools.hotel.mock_hotel_tool import MockHotelTool
from tools.hotel.real_hotel_tool import RealHotelTool
from tools.poi.base_poi_tool import BasePOITool
from tools.poi.mock_poi_tool import MockPOITool
from tools.poi.real_poi_tool import RealPOITool
from tools.search.base_search_tool import BaseSearchTool
from tools.search.mock_search_tool import MockSearchTool
from tools.search.real_search_tool import RealSearchTool
from tools.transport.base_transport_tool import BaseTransportTool
from tools.transport.mock_transport_tool import MockTransportTool
from tools.transport.real_transport_tool import RealTransportTool
from tools.weather.base_weather_tool import BaseWeatherTool
from tools.weather.mock_weather_tool import MockWeatherTool
from tools.weather.real_weather_tool import RealWeatherTool
from utils.logger import get_logger

logger = get_logger(__name__)


class _FallbackWeatherTool(BaseWeatherTool):
    name = "weather_tool"

    def __init__(self, primary: BaseWeatherTool, fallback: BaseWeatherTool) -> None:
        self.primary = primary
        self.fallback = fallback

    def get_weather(self, city: str, date: str):
        started = time.perf_counter()
        try:
            result = self.primary.get_weather(city, date)
            logger.info(
                "weather_api_hit source=real duration_ms=%.2f fallback=false city=%s date=%s",
                (time.perf_counter() - started) * 1000,
                city,
                date,
            )
            return result
        except Exception as exc:
            logger.warning(
                "weather_api_hit source=real duration_ms=%.2f fallback=true city=%s date=%s error=%s",
                (time.perf_counter() - started) * 1000,
                city,
                date,
                str(exc),
            )
            return {**self.fallback.get_weather(city, date), "fallback": True}


class _FallbackPOITool(BasePOITool):
    name = "poi_tool"

    def __init__(self, primary: BasePOITool, fallback: BasePOITool) -> None:
        self.primary = primary
        self.fallback = fallback

    def search_pois(self, city: str, preferences: list[str]):
        try:
            return self.primary.search_pois(city, preferences)
        except Exception:
            return self.fallback.search_pois(city, preferences)


class _FallbackHotelTool(BaseHotelTool):
    name = "hotel_tool"

    def __init__(self, primary: BaseHotelTool, fallback: BaseHotelTool) -> None:
        self.primary = primary
        self.fallback = fallback

    def search_hotels(
        self,
        city: str,
        checkin: str,
        checkout: str,
        budget_per_night: float | None = None,
    ):
        started = time.perf_counter()
        try:
            result = self.primary.search_hotels(city, checkin, checkout, budget_per_night)
            logger.info(
                "hotel_api_hit source=real duration_ms=%.2f fallback=false city=%s",
                (time.perf_counter() - started) * 1000,
                city,
            )
            return result
        except Exception as exc:
            logger.warning(
                "hotel_api_hit source=real duration_ms=%.2f fallback=true city=%s error=%s",
                (time.perf_counter() - started) * 1000,
                city,
                str(exc),
            )
            return [
                {**x, "fallback": True}
                for x in self.fallback.search_hotels(city, checkin, checkout, budget_per_night)
            ]


class _FallbackTransportTool(BaseTransportTool):
    name = "transport_tool"

    def __init__(self, primary: BaseTransportTool, fallback: BaseTransportTool) -> None:
        self.primary = primary
        self.fallback = fallback

    def estimate_route(self, origin: str, destination: str, mode: str = "taxi"):
        started = time.perf_counter()
        try:
            result = self.primary.estimate_route(origin, destination, mode)
            logger.info(
                "transport_api_hit source=real duration_ms=%.2f fallback=false origin=%s destination=%s mode=%s",
                (time.perf_counter() - started) * 1000,
                origin,
                destination,
                mode,
            )
            return result
        except Exception as exc:
            logger.warning(
                "transport_api_hit source=real duration_ms=%.2f fallback=true origin=%s destination=%s mode=%s error=%s",
                (time.perf_counter() - started) * 1000,
                origin,
                destination,
                mode,
                str(exc),
            )
            result = self.fallback.estimate_route(origin, destination, mode)
            return {**result, "fallback": True}


class _FallbackSearchTool(BaseSearchTool):
    name = "search_tool"

    def __init__(self, primary: BaseSearchTool, fallback: BaseSearchTool) -> None:
        self.primary = primary
        self.fallback = fallback

    def search(self, query: str, top_k: int = 5):
        started = time.perf_counter()
        try:
            result = self.primary.search(query, top_k)
            logger.info(
                "search_api_hit source=real duration_ms=%.2f fallback=false query=%s",
                (time.perf_counter() - started) * 1000,
                query,
            )
            return result
        except Exception as exc:
            logger.warning(
                "search_api_hit source=real duration_ms=%.2f fallback=true query=%s error=%s",
                (time.perf_counter() - started) * 1000,
                query,
                str(exc),
            )
            return [{**x, "fallback": "true"} for x in self.fallback.search(query, top_k)]


def get_weather_tool() -> BaseWeatherTool:
    mock = MockWeatherTool()
    if settings.USE_REAL_WEATHER_API:
        return _FallbackWeatherTool(primary=RealWeatherTool(), fallback=mock)
    return mock


def get_poi_tool() -> BasePOITool:
    mock = MockPOITool()
    if settings.USE_REAL_POI_API:
        return _FallbackPOITool(primary=RealPOITool(), fallback=mock)
    return mock


def get_hotel_tool() -> BaseHotelTool:
    mock = MockHotelTool()
    if settings.USE_REAL_HOTEL_API:
        return _FallbackHotelTool(primary=RealHotelTool(), fallback=mock)
    return mock


def get_transport_tool() -> BaseTransportTool:
    mock = MockTransportTool()
    if settings.USE_REAL_TRANSPORT_API:
        return _FallbackTransportTool(primary=RealTransportTool(), fallback=mock)
    return mock


def get_search_tool() -> BaseSearchTool:
    mock = MockSearchTool()
    if settings.USE_REAL_SEARCH_API:
        return _FallbackSearchTool(primary=RealSearchTool(), fallback=mock)
    return mock
