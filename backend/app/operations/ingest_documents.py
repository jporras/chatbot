import uuid
from typing import List
from io import BytesIO
from pypdf import PdfReader

CHUNK_SIZE = 500

class IngestDocuments:

    def __init__(self, vector_store, embedding_service):
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def _extract_text_from_pdf(self, file_bytes: bytes) -> List[str]:
        reader = PdfReader(BytesIO(file_bytes))
        texts = []

        for page in reader.pages:
            content = page.extract_text()
            if content:
                texts.append(content)

        return texts

    def _chunk_text(self, texts: List[str]) -> List[str]:
        chunks = []

        for text in texts:
            for i in range(0, len(text), CHUNK_SIZE):
                chunks.append(text[i:i + CHUNK_SIZE])

        return chunks

    def execute(self, files: List[bytes]) -> dict:

        all_texts = []

        for file_bytes in files:
            texts = self._extract_text_from_pdf(file_bytes)
            all_texts.extend(texts)

        chunks = self._chunk_text(all_texts)

        if not chunks:
            return {"documents_indexed": 0}

        ids = [str(uuid.uuid4()) for _ in chunks]
        metadata = [{"source": "pdf"} for _ in chunks]

        self.vector_store.add_documents(ids, chunks, metadata)

        return {"documents_indexed": len(chunks)}