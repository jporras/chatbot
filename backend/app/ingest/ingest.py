import uuid 
from typing import List 
from io import BytesIO 
from pypdf import PdfReader 

CHUNK_SIZE = 500 

class Ingest: 
    def __init__(self, vector): 
        self.vector = vector 
    
    def _extract_text_from_pdf(self, path: str) -> List[str]:
        reader = PdfReader(path, strict=False)
        texts = []
        for page in reader.pages:
            content = page.extract_text()
            if content:
                texts.append(content)
        return texts
    
    def _extract_text_from_md(self, path: str) -> List[str]:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return [text]
    
    def _chunk_text(self, texts: List[str]) -> List[str]: 
        chunks = [] 
        for text in texts: 
            for i in range(0, len(text), CHUNK_SIZE): 
                chunks.append(text[i:i + CHUNK_SIZE]) 
        return chunks 
    
    def execute(self, files: List[str]) -> dict:
        all_texts = []
        for path in files:
            if path.endswith(".pdf"):
                texts = self._extract_text_from_pdf(path)
            elif path.endswith(".md"):
                texts = self._extract_text_from_md(path)
            else:
                continue
            all_texts.extend(texts)
        chunks = self._chunk_text(all_texts)
        if not chunks:
            return {"documents_indexed": 0}

        ids = [str(uuid.uuid4()) for _ in chunks]
        metadata = [
            {"source": path}
            for path in files
            for _ in range(len(chunks) // len(files))
        ]
        self.vector.add_documents(ids, chunks, metadata)
        return {"documents_indexed": len(chunks)}
