from fastapi import FastAPI
from pydantic import BaseModel
from rag import generate_answer

app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Question):
    answer = generate_answer(q.question)
    return {"answer": answer}
