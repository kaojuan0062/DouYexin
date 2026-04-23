from __future__ import annotations

from memory.base import BaseSqliteStore
from memory.models import PreferenceMemoryRecord


class PreferenceMemoryStore(BaseSqliteStore[PreferenceMemoryRecord]):
    memory_type = "preference"

    def _lookup_keys(self, session_id: str, user_id: str | None) -> list[str]:
        keys: list[str] = []
        if user_id:
            keys.append(f"user:{user_id}")
        keys.append(f"session:{session_id}")
        return keys

    def _write_key(self, session_id: str, user_id: str | None) -> str:
        return f"user:{user_id}" if user_id else f"session:{session_id}"

    def _create_record(
        self,
        session_id: str,
        payload: dict,
        user_id: str | None,
    ) -> PreferenceMemoryRecord:
        return PreferenceMemoryRecord(
            session_id=session_id,
            user_id=user_id,
            payload=payload,
        )
