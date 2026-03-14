# app/routes/ask.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask(request: QuestionRequest):
    answer = Ask.execute(request.question)
    return {"answer": answer}