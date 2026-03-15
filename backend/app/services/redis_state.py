import json
from datetime import datetime, timezone
from typing import Any
import redis
from app.core.config import settings

class RedisStateService:
    def __init__(self) -> None:
        self.client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def set_document_status(
        self,
        document_id: str,
        *,
        batch_id: str,
        filename: str,
        file_version: int,
        status: str,
        progress: int,
        stage_message: str,
        error: str | None = None,
    ) -> None:
        payload = {
            "document_id": document_id,
            "batch_id": batch_id,
            "filename": filename,
            "file_version": file_version,
            "status": status,
            "progress": progress,
            "stage_message": stage_message,
            "error": error,
            "updated_at": self._now(),
        }
        self.client.set(f"doc:{document_id}:status", json.dumps(payload))
        self.client.sadd(f"batch:{batch_id}:documents", document_id)
        self.client.publish(f"stream:batch:{batch_id}", json.dumps(payload))

    def get_document_status(self, document_id: str) -> dict[str, Any] | None:
        raw = self.client.get(f"doc:{document_id}:status")
        return json.loads(raw) if raw else None

    def get_batch_documents(self, batch_id: str) -> list[str]:
        return sorted(self.client.smembers(f"batch:{batch_id}:documents"))

    def get_batch_status(self, batch_id: str) -> list[dict[str, Any]]:
        items = []
        for document_id in self.get_batch_documents(batch_id):
            status = self.get_document_status(document_id)
            if status:
                items.append(status)
        return items

    def publish_query_event(self, query_id: str, payload: dict[str, Any]) -> None:
        payload = {**payload, "query_id": query_id, "updated_at": self._now()}
        self.client.set(f"query:{query_id}:status", json.dumps(payload))
        self.client.publish(f"stream:query:{query_id}", json.dumps(payload))

    def get_query_status(self, query_id: str) -> dict[str, Any] | None:
        raw = self.client.get(f"query:{query_id}:status")
        return json.loads(raw) if raw else None