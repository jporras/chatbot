import json
from confluent_kafka import Producer

from app.core.config import settings


class KafkaProducerService:
    def __init__(self) -> None:
        self._producer = Producer(
            {"bootstrap.servers": settings.kafka_bootstrap_servers}
        )

    def publish(self, topic: str, message: dict, key: str | None = None) -> None:
        self._producer.produce(
            topic=topic,
            key=key,
            value=json.dumps(message, default=str).encode("utf-8"),
        )
        self._producer.flush()