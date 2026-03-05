# upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from app.operations.ingest_documents import IngestDocuments
from app.adapters.chroma_store import ChromaStore
from app.services.embedding_service import EmbeddingService

router = APIRouter()

def get_workflow():
    embedding_service = EmbeddingService()
    vector_store = ChromaStore(embedding_service)
    return IngestDocuments(vector_store, embedding_service)


@router.post("/upload")
async def upload(files: List[UploadFile] = File(...)):

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    workflow = get_workflow()

    file_bytes = []

    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF"
            )

        content = await file.read()
        file_bytes.append(content)

    result = workflow.execute(file_bytes)

    return result