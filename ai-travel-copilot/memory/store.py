from __future__ import annotations

from typing import Any, Dict

from memory.memory_service import memory_service


class MemoryStore:
    """兼容层：保留旧接口，内部转发到新的 MemoryService。"""

    def get_session(self, session_id: str) -> Dict[str, Any]:
        return memory_service.load_context(session_id=session_id).get("session", {})

    def update_session(self, session_id: str, payload: Dict[str, Any]) -> None:
        memory_service.session_store.upsert(session_id=session_id, payload=payload)

    def get_preference(self, session_id: str) -> Dict[str, Any]:
        return memory_service.load_context(session_id=session_id).get("preference", {})

    def update_preference(self, session_id: str, payload: Dict[str, Any]) -> None:
        memory_service.preference_store.upsert(session_id=session_id, payload=payload)

    def get_summary(self, session_id: str) -> Dict[str, Any]:
        return memory_service.load_context(session_id=session_id).get("summary", {})

    def update_summary(self, session_id: str, payload: Dict[str, Any]) -> None:
        memory_service.summary_store.upsert(session_id=session_id, payload=payload)


memory_store = MemoryStore()
