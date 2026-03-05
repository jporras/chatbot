# qdrant_store

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.domain.vector_store import VectorStore

class QdrantStore(VectorStore):

    def __init__(
        self,
        embedding_service,
        collection_name="documents",
        host="localhost",
        port=6333,
    ):
        self.embedding_service = embedding_service
        self.collection_name = collection_name

        self.client = QdrantClient(host=host, port=port)

        vector_size = self.embedding_service.dimension()
        self._ensure_collection(vector_size)

    def _ensure_collection(self, vector_size):
        collections = self.client.get_collections().collections
        existing = [c.name for c in collections]

        if self.collection_name not in existing:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )

    def add_documents(self, ids, documents, metadata):
        vectors = self.embedding_service.embed(documents)

        points = [
            PointStruct(
                id=ids[i],
                vector=vectors[i],
                payload={
                    "text": documents[i],
                    **metadata[i]
                }
            )
            for i in range(len(ids))
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def similarity_search(self, query_vector, k=3):
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=k
        )

        return [
            {
                "id": r.id,
                "document": r.payload["text"],
                "metadata": {
                    key: value
                    for key, value in r.payload.items()
                    if key != "text"
                }
            }
            for r in results
        ]