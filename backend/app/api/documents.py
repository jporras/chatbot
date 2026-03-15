from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.services.redis_state import RedisStateService
from app.services.sse import redis_pubsub_stream, sse_format

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/documents/{document_id}/status")
def get_document_status(document_id: str):
    state = RedisStateService()
    return state.get_document_status(document_id) or {"detail": "Not found"}


@router.get("/uploads/{batch_id}/status")
def get_batch_status(batch_id: str):
    state = RedisStateService()
    return {"batch_id": batch_id, "items": state.get_batch_status(batch_id)}


@router.get("/uploads/{batch_id}/stream")
async def stream_batch(batch_id: str):
    async def event_generator():
        state = RedisStateService()
        initial = state.get_batch_status(batch_id)
        yield sse_format("snapshot", {"batch_id": batch_id, "items": initial})
        async for event in redis_pubsub_stream(f"stream:batch:{batch_id}"):
            yield sse_format("document_status", event["data"])

    return StreamingResponse(event_generator(), media_type="text/event-stream")