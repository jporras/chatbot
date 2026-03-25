from threading import Lock

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    _model: SentenceTransformer | None = None
    _lock = Lock()

    def __init__(self) -> None:
        self.model = self._get_model()

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            with cls._lock:
                if cls._model is None:
                    cls._model = SentenceTransformer(
                        settings.rag_model,
                        use_auth_token=settings.hf_token or None,
                    )
        return cls._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()
