import asyncio
import json
from collections.abc import AsyncIterator

import redis

from app.core.config import settings


async def redis_pubsub_stream(channel: str) -> AsyncIterator[dict]:
    client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = client.pubsub()
    pubsub.subscribe(channel)

    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                yield {
                    "event": "message",
                    "data": message["data"],
                }
            await asyncio.sleep(0.5)
    finally:
        pubsub.close()
        client.close()


def sse_format(event: str, data: dict | list | str) -> str:
    payload = data if isinstance(data, str) else json.dumps(data, default=str)
    return f"event: {event}\ndata: {payload}\n\n"