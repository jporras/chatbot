# app/api/upload.py
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException 
from core.config import UPLOAD_FOLDER, TOPIC_DOCUMENT_UPLOADED
from typing import List
from app.services.kafka import send_event

router = APIRouter() 

@router.post("/upload") 
async def upload(files: List[UploadFile] = File(...)): 

    if not files: 
        raise HTTPException(status_code=400, detail="No files provided")
    
    processed = []
    for file in files: 

        document_id = str(uuid.uuid4())

        file_name = file.filename.lower() 
        if not (file_name.endswith(".pdf") or file_name.endswith(".md")): 
            raise HTTPException( status_code=400, detail=f"{file.filename} must be PDF or Markdown" ) 
        
        content = await file.read() 

        if not content: 
            raise HTTPException( status_code=400, detail=f"{file.filename} is empty" ) 
        
        unique_file_name = f"{document_id}_{file_name}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_file_name)

        with open(file_path, "wb") as f:
            f.write(content)

        event = {
            "document_id": document_id,
            "filename": file_name,
            "path": file_path
        }

        send_event(TOPIC_DOCUMENT_UPLOADED, event)

        processed.append({
            "document_id": document_id,
            "filename": file_name
        })

    return {"status": "success", "files": processed}
