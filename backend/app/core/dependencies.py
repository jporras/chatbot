# app/core/dependencies.py
from app.store.chroma import Chroma
from app.services.embedding import Embedding
from app.services.ingest import Ingest
from app.services.rag import RAG
from app.services.llm import LLM

embedding = Embedding()

vector = Chroma(
    embedding=embedding
)

ingest = Ingest(
    vector=vector,
)

rag = RAG(
    vector=vector,
    llm=LLM()
)
