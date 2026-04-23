from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

MemoryType = Literal["session", "preference", "summary", "research"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryRecord(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    memory_type: MemoryType
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()


class SessionMemoryRecord(MemoryRecord):
    memory_type: Literal["session"] = "session"


class PreferenceMemoryRecord(MemoryRecord):
    memory_type: Literal["preference"] = "preference"


class SummaryMemoryRecord(MemoryRecord):
    memory_type: Literal["summary"] = "summary"


class ResearchMemoryRecord(MemoryRecord):
    memory_type: Literal["research"] = "research"
