# vector_store.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VectorStore(ABC):

    @abstractmethod
    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadata: List[Dict[str, Any]]
    ):
        pass

    @abstractmethod
    def similarity_search(
        self,
        query_vector: List[float],
        k: int = 3
    ) -> List[Dict[str, Any]]:
        pass