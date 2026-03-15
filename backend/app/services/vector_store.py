import chromadb

from app.core.config import settings


class VectorStoreService:
    def __init__(self) -> None:
        client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        self.collection = client.get_or_create_collection(
            name=settings.chroma_collection
        )

    def add_chunks(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def similarity_search(self, query_embedding: list[float], k: int = 5) -> dict:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where={"is_latest": True},
        )