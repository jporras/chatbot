# app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException 
from typing import List

from backend.app.services.ingest import Ingest 

router = APIRouter() 

@router.post("/upload") 
async def upload(files: List[UploadFile] = File(...)): 
    if not files: 
        raise HTTPException(status_code=400, detail="No files provided") 
    file_bytes = [] 
    for file in files: 
        filename = file.filename.lower() 
        if not (filename.endswith(".pdf") or filename.endswith(".md")): 
            raise HTTPException( status_code=400, detail=f"{file.filename} must be PDF or Markdown" ) 
        content = await file.read() 
        if not content: 
            raise HTTPException( status_code=400, detail=f"{file.filename} is empty" ) 
        file_bytes.append(content) 
        result = Ingest.execute(file_bytes) 
        return result