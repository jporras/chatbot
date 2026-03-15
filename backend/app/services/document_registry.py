import redis

from app.core.config import settings


class DocumentRegistryService:
    def __init__(self) -> None:
        self.client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def reserve_next_version(self, document_id: str) -> int:
        return int(self.client.incr(f"doc:{document_id}:latest_version"))

    def set_current_hash(self, document_id: str, file_version: int, content_hash: str) -> None:
        self.client.set(
            f"doc:{document_id}:v:{file_version}:content_hash",
            content_hash,
        )