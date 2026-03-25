import re
from typing import Any


WORD_RE = re.compile(r"[a-zA-Z0-9áéíóúñÁÉÍÓÚÑ]+")


class RerankerService:
    def _tokenize(self, text: str) -> set[str]:
        return {w.lower() for w in WORD_RE.findall(text)}

    def rerank(
        self,
        *,
        question: str,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        distances: list[float] | None = None,
        top_k: int = 5,
    ) -> tuple[list[str], list[dict[str, Any]]]:
        if not documents:
            return [], []

        q_tokens = self._tokenize(question)
        rows: list[tuple[float, str, dict[str, Any]]] = []

        for i, doc in enumerate(documents):
            d_tokens = self._tokenize(doc)
            overlap = len(q_tokens & d_tokens)
            lexical = overlap / max(1, len(q_tokens))
            distance = distances[i] if distances and i < len(distances) else 0.5
            vector_score = 1.0 / (1.0 + max(0.0, distance))
            final_score = (0.65 * vector_score) + (0.35 * lexical)
            metadata = {**metadatas[i], "rerank_score": round(final_score, 6)}
            rows.append((final_score, doc, metadata))

        rows.sort(key=lambda x: x[0], reverse=True)
        top = rows[:top_k]
        reranked_docs = [item[1] for item in top]
        reranked_meta = [item[2] for item in top]
        return reranked_docs, reranked_meta
