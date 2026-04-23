from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_route_optimization_outputs_travel_fields() -> None:
    payload = {
        "origin": "北京",
        "destination": "上海",
        "days": 3,
        "budget": 3500,
        "preferences": ["历史", "夜景"],
        "constraints": {"pace": "紧凑", "indoor_first": False},
        "session_id": "test-route-opt",
    }
    resp = client.post("/plan/generate", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    day1 = data["daily_plan"][0]
    assert day1["travel_time_estimate"] >= 0
    assert "推荐顺序" in day1["route_notes"]
    assert day1["transport_suggestion"] != ""
