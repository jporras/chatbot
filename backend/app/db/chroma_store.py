# chroma_store.py

import chromadb
from backend.app.db.vector_store import VectorStore

class ChromaStore(VectorStore):

    def __init__(
        self,
        embedding_service,
        collection_name="documents",
        persist_dir="./chroma_data"
    ):
        self.embedding_service = embedding_service

        self.client = chromadb.Client(
            chromadb.config.Settings(
                persist_directory=persist_dir,
                is_persistent=True
            )
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_documents(self, ids, documents, metadata):
        vectors = self.embedding_service.embed(documents)

        self.collection.add(
            ids=ids,
            embeddings=vectors,
            documents=documents,
            metadatas=metadata
        )

    def similarity_search(self, query_vector, k=3):
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )

        return [
            {
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i]
            }
            for i in range(len(results["ids"][0]))
        ]