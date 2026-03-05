# embedding_service.py

from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def dimension(self):
        return self._dimension