from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_replan_partial_update_by_affected_days() -> None:
    current_plan = {
        "summary": "示例计划",
        "daily_plan": [
            {"day": 1, "weather": "晴 26℃", "activities": ["A", "B", "C", "D"], "transport_tip": "地铁+步行"},
            {"day": 2, "weather": "小雨 22℃", "activities": ["E", "F", "G", "H"], "transport_tip": "地铁+步行"},
            {"day": 3, "weather": "多云 24℃", "activities": ["I", "J", "K", "L"], "transport_tip": "地铁+步行"},
        ],
        "estimated_budget": {
            "total": 3000,
            "by_category": {"hotel": 1200, "food": 750, "transport": 510, "tickets": 300, "misc": 240},
            "daily_average": 1000,
            "within_budget": True,
            "warning": None,
            "preference_tags": ["美食", "夜景"],
            "hotel_recommendations": [],
            "budget_breakdown": {},
            "over_budget_flag": False,
            "optimization_suggestions": [],
        },
        "notes": ["mock plan"],
        "meta": {},
    }

    payload = {
        "original_request": {
            "origin": "上海",
            "destination": "杭州",
            "days": 3,
            "budget": 3000,
            "preferences": ["美食", "夜景"],
            "constraints": {"pace": "轻松", "indoor_first": False},
            "session_id": "test-replan-session",
        },
        "current_plan": current_plan,
        "affected_days": [2],
        "locked_days": [1],
        "reason": "rain",
        "keep_budget": True,
        "keep_hotel": True,
        "keep_confirmed_segments": True,
        "food_focus": True,
        "session_id": "test-replan-session",
    }

    resp = client.post("/plan/replan", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["daily_plan"][0]["activities"] == ["A", "B", "C", "D"]
    assert "室内" in data["daily_plan"][1]["activities"][0]
    assert data["daily_plan"][2]["activities"] == ["I", "J", "K", "L"]

    assert "replanning_diff" in data
    assert len(data["replanning_diff"]["changed_segments"]) == 1
    assert data["replanning_diff"]["changed_segments"][0]["day"] == 2
    assert "reused_memory_summary" in data
    assert "preserved_constraints" in data
