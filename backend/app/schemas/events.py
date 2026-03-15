from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ChunkPayload(BaseModel):
    chunk_id: str
    chunk_index: int
    text: str
    metadata: Dict[str, Any]


class DocumentUploadedPayload(BaseModel):
    batch_id: str
    document_id: str
    file_version: int
    filename: str
    path: str
    content_hash: str
    content_type: Optional[str] = None
    uploaded_by: str = "anonymous"


class DocumentChunkedPayload(BaseModel):
    batch_id: str
    document_id: str
    file_version: int
    filename: str
    content_hash: str
    chunks: List[ChunkPayload]


class DocumentIndexedPayload(BaseModel):
    batch_id: str
    document_id: str
    file_version: int
    chunks_indexed: int
    embedding_model: str


class DocumentFailedPayload(BaseModel):
    batch_id: Optional[str] = None
    document_id: str
    file_version: Optional[int] = None
    stage: str
    error: str


class QueryStartedPayload(BaseModel):
    query_id: str
    question: str


class QueryProgressPayload(BaseModel):
    query_id: str
    stage: str
    message: str
    progress: int


class QueryFinishedPayload(BaseModel):
    query_id: str
    answer: str
    sources: List[Dict[str, Any]]


class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: Literal[
        "document.uploaded",
        "document.chunked",
        "document.indexed",
        "document.failed",
        "query.started",
        "query.progress",
        "query.finished",
        "query.failed",
    ]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str
    pipeline_version: str
    payload: Dict[str, Any]