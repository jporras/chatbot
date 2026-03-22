from threading import Thread
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.api import AskAcceptedResponse, AskRequest
from app.services.query_service import QueryService
from app.services.redis_state import RedisStateService
from app.services.sse import redis_pubsub_stream, sse_format

router = APIRouter(prefix="/api", tags=["ask"])


def _run_query(
    query_id: str,
    question: str,
    *,
    user_id: str,
    session_id: str,
    metadata_filter: dict | None,
):
    service = QueryService()
    state = RedisStateService()
    try:
        service.ask(
            query_id,
            question,
            user_id=user_id,
            session_id=session_id,
            metadata_filter=metadata_filter,
        )
    except Exception as exc:
        state.publish_query_event(query_id, {
            "status": "FAILED",
            "progress": 100,
            "message": str(exc),
        })


@router.post("/ask", response_model=AskAcceptedResponse)
def ask_question(request: AskRequest):
    query_id = str(uuid4())
    session_id = request.session_id or "default"
    state = RedisStateService()
    state.publish_query_event(query_id, {
        "status": "QUEUED",
        "progress": 0,
        "message": "Pregunta encolada",
    })
    Thread(
        target=_run_query,
        kwargs={
            "query_id": query_id,
            "question": request.question,
            "user_id": request.user_id,
            "session_id": session_id,
            "metadata_filter": request.metadata_filter,
        },
        daemon=True,
    ).start()
    return AskAcceptedResponse(query_id=query_id, status="QUEUED")


@router.get("/queries/{query_id}/status")
def get_query_status(query_id: str):
    state = RedisStateService()
    status = state.get_query_status(query_id)
    if not status:
        raise HTTPException(status_code=404, detail="Query not found")
    return status


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
