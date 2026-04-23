from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_generate_plan_success() -> None:
    payload = {
        "origin": "上海",
        "destination": "杭州",
        "days": 3,
        "budget": 3000,
        "preferences": ["美食", "夜景"],
        "constraints": {"pace": "轻松", "indoor_first": False},
        "session_id": "test-generate-session",
    }
    resp = client.post("/plan/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "summary" in data
    assert len(data["daily_plan"]) == 3
    assert data["estimated_budget"]["total"] > 0
    assert "hotel_recommendations" in data
    assert "budget_breakdown" in data
    assert "meta" in data and "metrics" in data["meta"]

    assert "normalized_requirements" in data
    assert "query_rewrites" in data
    assert "source_summary" in data
    assert "recommendation_reasons" in data
    assert "candidate_pool_summary" in data
    assert "research_memory_hit" in data
    assert "reused_candidates_count" in data
    assert "refreshed_queries" in data
    assert "cache_strategy" in data
