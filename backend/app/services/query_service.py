from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.ollama_client import OllamaClient
from app.services.redis_state import RedisStateService
from app.services.vector_store import VectorStoreService


class QueryService:
    def __init__(self) -> None:
        self.embedder = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.llm = OllamaClient()
        self.state = RedisStateService()

    def ask(self, query_id: str, question: str) -> dict:
        self.state.publish_query_event(query_id, {
            "status": "RECEIVED",
            "progress": 5,
            "message": "Pregunta recibida",
        })

        self.state.publish_query_event(query_id, {
            "status": "EMBEDDING_QUERY",
            "progress": 20,
            "message": "Generando embedding de la pregunta",
        })
        query_embedding = self.embedder.embed_query(question)

        self.state.publish_query_event(query_id, {
            "status": "RETRIEVAL",
            "progress": 45,
            "message": "Buscando contexto relevante",
        })
        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            k=settings.retrieval_top_k,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        context = "\n\n".join(documents)

        self.state.publish_query_event(query_id, {
            "status": "PROMPT_BUILD",
            "progress": 65,
            "message": "Construyendo prompt con el contexto recuperado",
        })
        prompt = f"""
Responde usando solo el contexto proporcionado.
Si no hay suficiente información, dilo explícitamente.

Pregunta:
{question}

Contexto:
{context}
""".strip()

        self.state.publish_query_event(query_id, {
            "status": "GENERATING",
            "progress": 85,
            "message": f"Generando respuesta con {settings.llm_model}",
        })
        answer = self.llm.generate(prompt)

        final_payload = {
            "status": "DONE",
            "progress": 100,
            "message": "Respuesta lista",
            "answer": answer,
            "sources": metadatas,
        }
        self.state.publish_query_event(query_id, final_payload)

        return {
            "answer": answer,
            "sources": metadatas,
        }