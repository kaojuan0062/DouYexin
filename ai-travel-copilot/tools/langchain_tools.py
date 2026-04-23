from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from config.settings import settings
from tools.tool_factory import (
    get_hotel_tool,
    get_search_tool,
    get_transport_tool,
    get_weather_tool,
)


@tool("search_tool")
def search_tool(query: str) -> str:
    """Search travel-related web results by query."""
    results = get_search_tool().search(query=query, top_k=5)
    return json.dumps(results, ensure_ascii=False)


@tool("weather_tool")
def weather_tool(city_date: str) -> str:
    """Get weather using 'city|date' formatted input."""
    city, date = (city_date.split("|", 1) + [""])[:2]
    result = get_weather_tool().get_weather(city=city.strip(), date=date.strip())
    return json.dumps(result, ensure_ascii=False)


@tool("hotel_tool")
def hotel_tool(query: str) -> str:
    """Search hotels using 'city|checkin|checkout|budget_per_night'."""
    city, checkin, checkout, budget = (query.split("|", 3) + ["", "", "", ""])[:4]
    budget_value = float(budget) if budget.strip() else None
    result = get_hotel_tool().search_hotels(
        city=city.strip(),
        checkin=checkin.strip(),
        checkout=checkout.strip(),
        budget_per_night=budget_value,
    )
    return json.dumps(result, ensure_ascii=False)


@tool("transport_tool")
def transport_tool(route: str) -> str:
    """Estimate route using 'origin|destination|mode'."""
    origin, destination, mode = (route.split("|", 2) + ["", "", "taxi"])[:3]
    result = get_transport_tool().estimate_route(
        origin=origin.strip(),
        destination=destination.strip(),
        mode=(mode or "taxi").strip(),
    )
    return json.dumps(result, ensure_ascii=False)


LANGCHAIN_TOOLS = [search_tool, weather_tool, hotel_tool, transport_tool]


def is_langchain_tool_mode_enabled() -> bool:
    return bool(settings.LANGCHAIN_TOOL_MODE)


def get_langchain_tools() -> list[Any]:
    return LANGCHAIN_TOOLS
