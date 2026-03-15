from threading import Thread
from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.rag.query_service import QueryService
from app.schemas.api import AskAcceptedResponse, AskRequest
from app.services.redis_state import RedisStateService
from app.services.sse import redis_pubsub_stream, sse_format

router = APIRouter(prefix="/api", tags=["ask"])


def _run_query(query_id: str, question: str):
    service = QueryService()
    state = RedisStateService()
    try:
        service.ask(query_id, question)
    except Exception as exc:
        state.publish_query_event(query_id, {
            "status": "FAILED",
            "progress": 100,
            "message": str(exc),
        })


@router.post("/ask", response_model=AskAcceptedResponse)
def ask_question(request: AskRequest):
    query_id = str(uuid4())
    state = RedisStateService()
    state.publish_query_event(query_id, {
        "status": "QUEUED",
        "progress": 0,
        "message": "Pregunta encolada",
    })
    Thread(target=_run_query, args=(query_id, request.question), daemon=True).start()
    return AskAcceptedResponse(query_id=query_id, status="QUEUED")


@router.get("/queries/{query_id}/status")
def get_query_status(query_id: str):
    state = RedisStateService()
    return state.get_query_status(query_id) or {"detail": "Not found"}


@router.get("/queries/{query_id}/stream")
async def stream_query(query_id: str):
    async def event_generator():
        state = RedisStateService()
        current = state.get_query_status(query_id)
        if current:
            yield sse_format("snapshot", current)
        async for event in redis_pubsub_stream(f"stream:query:{query_id}"):
            yield sse_format("query_status", event["data"])

    return StreamingResponse(event_generator(), media_type="text/event-stream")