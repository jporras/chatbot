import chromadb
from typing import List, Dict, Any
from app.storage.vector import Vector

class Chroma(Vector):

    def __init__(self, path: str = "./chroma-data", collection_name: str = "documents"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add_embeddings(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ):

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadata
        )

    def similarity_search(self, query_vector: List[float], k: int = 3):
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )

        output = []

        for i in range(len(results["documents"][0])):
            output.append({
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return output