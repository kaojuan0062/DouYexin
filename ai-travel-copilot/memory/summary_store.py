from __future__ import annotations

from memory.base import BaseSqliteStore
from memory.models import SummaryMemoryRecord


class SummaryMemoryStore(BaseSqliteStore[SummaryMemoryRecord]):
    memory_type = "summary"

    def _lookup_keys(self, session_id: str, user_id: str | None) -> list[str]:
        return [f"session:{session_id}"]

    def _write_key(self, session_id: str, user_id: str | None) -> str:
        return f"session:{session_id}"

    def _create_record(
        self,
        session_id: str,
        payload: dict,
        user_id: str | None,
    ) -> SummaryMemoryRecord:
        return SummaryMemoryRecord(
            session_id=session_id,
            user_id=user_id,
            payload=payload,
        )
