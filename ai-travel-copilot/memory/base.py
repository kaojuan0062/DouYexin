from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Generic, Optional, TypeVar

from memory.models import MemoryRecord

RecordT = TypeVar("RecordT", bound=MemoryRecord)
_DB_PATH = Path(__file__).resolve().parent.parent / "memory.db"


class BaseMemoryStore(ABC, Generic[RecordT]):
    @abstractmethod
    def get(self, session_id: str, user_id: str | None = None) -> Optional[RecordT]:
        raise NotImplementedError

    @abstractmethod
    def upsert(
        self,
        session_id: str,
        payload: dict,
        user_id: str | None = None,
    ) -> RecordT:
        raise NotImplementedError


class BaseInMemoryStore(BaseMemoryStore[RecordT], Generic[RecordT]):
    def __init__(self) -> None:
        self._data: dict[str, RecordT] = {}
        self._lock = Lock()

    @abstractmethod
    def _create_record(
        self,
        session_id: str,
        payload: dict,
        user_id: str | None,
    ) -> RecordT:
        raise NotImplementedError

    def _write_key(self, session_id: str, user_id: str | None) -> str:
        return f"session:{session_id}"

    def _lookup_keys(self, session_id: str, user_id: str | None) -> list[str]:
        keys = []
        if user_id:
            keys.append(f"user:{user_id}")
        keys.append(f"session:{session_id}")
        return keys

    def get(self, session_id: str, user_id: str | None = None) -> Optional[RecordT]:
        with self._lock:
            for key in self._lookup_keys(session_id=session_id, user_id=user_id):
                record = self._data.get(key)
                if record:
                    return record.model_copy(deep=True)
        return None

    def upsert(
        self,
        session_id: str,
        payload: dict,
        user_id: str | None = None,
    ) -> RecordT:
        key = self._write_key(session_id=session_id, user_id=user_id)
        with self._lock:
            current = self._data.get(key)
            if current:
                current.payload.update(deepcopy(payload))
                current.touch()
                stored = current
            else:
                stored = self._create_record(
                    session_id=session_id,
                    payload=deepcopy(payload),
                    user_id=user_id,
                )
                self._data[key] = stored
            return stored.model_copy(deep=True)


class BaseSqliteStore(BaseMemoryStore[RecordT], Generic[RecordT]):
    def __init__(self) -> None:
        self._lock = Lock()
        self._db_path = _DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @property
    @abstractmethod
    def memory_type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _create_record(
        self,
        session_id: str,
        payload: dict,
        user_id: str | None,
    ) -> RecordT:
        raise NotImplementedError

    def _write_key(self, session_id: str, user_id: str | None) -> str:
        return f"session:{session_id}"

    def _lookup_keys(self, session_id: str, user_id: str | None) -> list[str]:
        keys = []
        if user_id:
            keys.append(f"user:{user_id}")
        keys.append(f"session:{session_id}")
        return keys

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    memory_type TEXT NOT NULL,
                    store_key TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (memory_type, store_key)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_records_session ON memory_records(session_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_records_user ON memory_records(user_id)"
            )

    def _row_to_record(self, row: sqlite3.Row) -> RecordT:
        payload = json.loads(row["payload_json"])
        return self._create_record(
            session_id=row["session_id"],
            payload=payload,
            user_id=row["user_id"],
        )

    def get(self, session_id: str, user_id: str | None = None) -> Optional[RecordT]:
        with self._lock:
            with self._connect() as conn:
                for key in self._lookup_keys(session_id=session_id, user_id=user_id):
                    row = conn.execute(
                        "SELECT session_id, user_id, payload_json FROM memory_records WHERE memory_type = ? AND store_key = ?",
                        (self.memory_type, key),
                    ).fetchone()
                    if row:
                        return self._row_to_record(row)
        return None

    def upsert(
        self,
        session_id: str,
        payload: dict,
        user_id: str | None = None,
    ) -> RecordT:
        key = self._write_key(session_id=session_id, user_id=user_id)
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT session_id, user_id, payload_json, created_at FROM memory_records WHERE memory_type = ? AND store_key = ?",
                    (self.memory_type, key),
                ).fetchone()
                if row:
                    current_payload = json.loads(row["payload_json"])
                    current_payload.update(deepcopy(payload))
                    conn.execute(
                        """
                        UPDATE memory_records
                        SET payload_json = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE memory_type = ? AND store_key = ?
                        """,
                        (json.dumps(current_payload, ensure_ascii=False), self.memory_type, key),
                    )
                    stored_payload = current_payload
                else:
                    stored_payload = deepcopy(payload)
                    conn.execute(
                        """
                        INSERT INTO memory_records(memory_type, store_key, session_id, user_id, payload_json, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """,
                        (
                            self.memory_type,
                            key,
                            session_id,
                            user_id,
                            json.dumps(stored_payload, ensure_ascii=False),
                        ),
                    )
        return self._create_record(session_id=session_id, payload=stored_payload, user_id=user_id)
