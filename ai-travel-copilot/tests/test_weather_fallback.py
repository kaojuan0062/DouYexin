from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_weather_fallback_is_used() -> None:
    payload = {
        "origin": "上海",
        "destination": "杭州",
        "days": 2,
        "budget": 2000,
        "preferences": ["美食"],
        "constraints": {"pace": "轻松", "indoor_first": False},
        "session_id": "test-weather-fallback",
    }
    resp = client.post("/plan/generate", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "tool_usage_summary" in data
    assert "fallback_used" in data["tool_usage_summary"]
    assert "weather" in data["tool_usage_summary"]["fallback_used"]
