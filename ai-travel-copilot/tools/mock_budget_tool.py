from typing import Dict, List, Literal


def estimate_budget(
    total_budget: float,
    days: int,
    preferences: List[str],
    pace: Literal["轻松", "紧凑"] = "轻松",
) -> Dict:
    hotel = total_budget * 0.4
    food_ratio = 0.28 if pace == "紧凑" else 0.25
    transport_ratio = 0.17 if pace == "轻松" else 0.2
    tickets = total_budget * 0.1

    food = total_budget * food_ratio
    transport = total_budget * transport_ratio
    misc = total_budget - hotel - food - transport - tickets

    within_budget = misc >= 0
    warning = None if within_budget else "当前节奏下预算偏紧，建议降低活动密度或提高预算。"

    return {
        "total": round(total_budget, 2),
        "by_category": {
            "hotel": round(hotel, 2),
            "food": round(food, 2),
            "transport": round(transport, 2),
            "tickets": round(tickets, 2),
            "misc": round(misc, 2),
        },
        "daily_average": round(total_budget / days, 2),
        "within_budget": within_budget,
        "warning": warning,
        "preference_tags": preferences,
    }
