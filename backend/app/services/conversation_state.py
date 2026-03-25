import json
from datetime import datetime, timezone
from typing import Any

import redis

from app.core.config import settings


class ConversationStateService:
    def __init__(self) -> None:
        self.client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def add_turn(
        self,
        *,
        user_id: str,
        session_id: str,
        role: str,
        text: str,
        sources: list[dict[str, Any]] | None = None,
    ) -> None:
        payload = {
            "role": role,
            "text": text,
            "sources": sources or [],
            "created_at": self._now(),
        }
        self.client.rpush(f"conv:{user_id}:{session_id}:history", json.dumps(payload))
        self.client.ltrim(f"conv:{user_id}:{session_id}:history", -settings.conversation_history_limit, -1)

    def get_history(self, *, user_id: str, session_id: str) -> list[dict[str, Any]]:
        items = self.client.lrange(f"conv:{user_id}:{session_id}:history", 0, -1)
        return [json.loads(item) for item in items]

    def set_user_state(self, *, user_id: str, state: dict[str, Any]) -> None:
        self.client.set(f"user:{user_id}:state", json.dumps(state))

    def get_user_state(self, *, user_id: str) -> dict[str, Any]:
        raw = self.client.get(f"user:{user_id}:state")
        return json.loads(raw) if raw else {}

    def merge_persistent_context(self, *, user_id: str, context: dict[str, Any]) -> dict[str, Any]:
        current = self.get_user_state(user_id=user_id)
        merged = {**current, **context, "updated_at": self._now()}
        self.set_user_state(user_id=user_id, state=merged)
        return merged
