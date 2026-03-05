from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.operations.ask_questions import AskQuestion
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService
from app.adapters.chroma_store import ChromaStore

router = APIRouter()

class Question(BaseModel):
    question: str


def get_workflow():
    embedding_service = EmbeddingService()
    vector_store = ChromaStore(embedding_service)
    rag_service = RAGService(vector_store, embedding_service)
    return AskQuestion(rag_service)


@router.post("/ask")
def ask(
    q: Question,
    workflow: AskQuestion = Depends(get_workflow)
):
    answer = workflow.execute(q.question)
    return {"answer": answer}