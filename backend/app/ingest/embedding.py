import os
from sentence_transformers import SentenceTransformer

class Embedding:
    def __init__(self):
        self.model = SentenceTransformer(os.getenv("rag_model"))
        self._dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str):
        return self.embed([text])[0]

    def embed_documents(self, texts: list[str]):
        return self.embed(texts)

    def dimension(self):
        return self._dimension