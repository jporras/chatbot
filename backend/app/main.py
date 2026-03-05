from fastapi import FastAPI

from app.api.routes.upload import router as upload_router
from app.api.routes.ask import router as ask_router

app = FastAPI(title="RAG Service")

app.include_router(upload_router, prefix="/api", tags=["Ingestion"])
app.include_router(ask_router, prefix="/api", tags=["QA"])