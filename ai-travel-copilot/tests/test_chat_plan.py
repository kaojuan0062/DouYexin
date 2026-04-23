from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


def test_chat_plan_success() -> None:
    payload = {
        "user_input": "下周想和女朋友去杭州玩两天，别太赶，预算两千多，想吃本地特色，酒店地铁方便",
        "session_id": "test-chat-session",
    }
    resp = client.post("/plan/chat", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert "normalized_requirements" in data
    assert "rewritten_queries" in data
    assert "research_summary" in data
    assert "recommended_candidates" in data
    assert "memory_applied" in data
    assert "inherited_preferences" in data
    assert "overridden_preferences" in data
    assert "research_memory_hit" in data
    assert "reused_candidates_count" in data
    assert "refreshed_queries" in data
    assert "cache_strategy" in data
    assert "final_plan" in data
    assert data["final_plan"]["summary"] != ""
