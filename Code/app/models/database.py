"""JSON file-based database layer following the ER diagram."""
import json
import uuid
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.config import STORAGE_DIR

_lock = threading.Lock()

COLLECTIONS = [
    "users",
    "user_queries",
    "ai_responses",
    "quizzes",
    "summaries",
    "learning_paths",
    "bookmarks",
    "documents",
    "user_settings",
    "flashcards",
    "analytics",
]


def _file_path(collection: str) -> Path:
    return STORAGE_DIR / f"{collection}.json"


def _ensure_collections() -> None:
    for name in COLLECTIONS:
        path = _file_path(name)
        if not path.exists():
            path.write_text("[]", encoding="utf-8")


def _read(collection: str) -> list[dict]:
    _ensure_collections()
    path = _file_path(collection)
    with _lock:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []


def _write(collection: str, data: list[dict]) -> None:
    _ensure_collections()
    path = _file_path(collection)
    with _lock:
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def new_id() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_all(collection: str, **filters) -> list[dict]:
    records = _read(collection)
    if not filters:
        return records
    result = []
    for record in records:
        if all(record.get(k) == v for k, v in filters.items()):
            result.append(record)
    return result


def find_one(collection: str, **filters) -> Optional[dict]:
    matches = find_all(collection, **filters)
    return matches[0] if matches else None


def insert(collection: str, record: dict) -> dict:
    records = _read(collection)
    records.append(record)
    _write(collection, records)
    return record


def update(collection: str, record_id: str, id_field: str, updates: dict) -> Optional[dict]:
    records = _read(collection)
    for i, record in enumerate(records):
        if record.get(id_field) == record_id:
            records[i] = {**record, **updates}
            _write(collection, records)
            return records[i]
    return None


def delete(collection: str, record_id: str, id_field: str) -> bool:
    records = _read(collection)
    new_records = [r for r in records if r.get(id_field) != record_id]
    if len(new_records) == len(records):
        return False
    _write(collection, new_records)
    return True


def delete_where(collection: str, **filters) -> int:
    records = _read(collection)
    new_records = [
        r for r in records
        if not all(r.get(k) == v for k, v in filters.items())
    ]
    removed = len(records) - len(new_records)
    if removed:
        _write(collection, new_records)
    return removed


def count(collection: str, **filters) -> int:
    return len(find_all(collection, **filters))
