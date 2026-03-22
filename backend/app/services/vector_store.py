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

    def similarity_search(
        self,
        *,
        query_embedding: list[float],
        k: int = 5,
        where: dict | None = None,
    ) -> dict:
        filters = {"is_latest": True, **(where or {})}
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filters,
        )

    def keyword_search(
        self,
        *,
        question: str,
        k: int = 5,
        where: dict | None = None,
    ) -> dict:
        filters = {"is_latest": True, **(where or {})}
        return self.collection.query(
            query_texts=[question],
            n_results=k,
            where=filters,
        )

    def hybrid_search(
        self,
        *,
        question: str,
        query_embedding: list[float],
        k: int,
        candidate_k: int,
        where: dict | None = None,
    ) -> dict:
        vector = self.similarity_search(query_embedding=query_embedding, k=candidate_k, where=where)
        keyword = self.keyword_search(question=question, k=candidate_k, where=where)

        docs = (vector.get("documents", [[]])[0] or []) + (keyword.get("documents", [[]])[0] or [])
        metas = (vector.get("metadatas", [[]])[0] or []) + (keyword.get("metadatas", [[]])[0] or [])
        dists = (vector.get("distances", [[]])[0] or []) + (keyword.get("distances", [[]])[0] or [])

        dedup: dict[str, tuple[dict, float]] = {}
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else 1.0
            key = meta.get("chunk_hash") or doc
            if key not in dedup or dist < dedup[key][1]:
                dedup[key] = ({"document": doc, "metadata": meta}, dist)

        ordered = sorted(dedup.values(), key=lambda row: row[1])[:k]
        return {
            "documents": [[item[0]["document"] for item in ordered]],
            "metadatas": [[item[0]["metadata"] for item in ordered]],
            "distances": [[item[1] for item in ordered]],
        }
