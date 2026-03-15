from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Vector(ABC):

    @abstractmethod
    def add_embeddings(
        self,
        ids: List[str],
        embeddings: List[List[float]],
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