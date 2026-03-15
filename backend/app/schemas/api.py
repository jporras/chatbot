from typing import Any

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class AskAcceptedResponse(BaseModel):
    query_id: str
    status: str


class QueryFinalResponse(BaseModel):
    answer: str
    sources: list[dict[str, Any]] = []


class UploadAcceptedItem(BaseModel):
    filename: str
    document_id: str
    file_version: int
    correlation_id: str
    batch_id: str
    status: str


class UploadAcceptedResponse(BaseModel):
    batch_id: str
    items: list[UploadAcceptedItem]