from app.core.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.conversation_state import ConversationStateService
from app.services.ollama_client import OllamaClient
from app.services.reranker import RerankerService
from app.services.redis_state import RedisStateService
from app.services.vector_store import VectorStoreService


class QueryService:
    def __init__(self) -> None:
        self.embedder = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.llm = OllamaClient()
        self.state = RedisStateService()
        self.reranker = RerankerService()
        self.conversations = ConversationStateService()

    def ask(
        self,
        query_id: str,
        question: str,
        *,
        user_id: str = "anonymous",
        session_id: str = "default",
        metadata_filter: dict | None = None,
    ) -> dict:
        self.state.publish_query_event(query_id, {
            "status": "RECEIVED",
            "progress": 5,
            "message": "Pregunta recibida",
        })
        self.conversations.add_turn(
            user_id=user_id,
            session_id=session_id,
            role="user",
            text=question,
        )

        self.state.publish_query_event(query_id, {
            "status": "EMBEDDING_QUERY",
            "progress": 20,
            "message": "Generando embedding de la pregunta",
        })
        query_embedding = self.embedder.embed_query(question)

        self.state.publish_query_event(query_id, {
            "status": "HYBRID_RETRIEVAL",
            "progress": 40,
            "message": "Buscando contexto con búsqueda híbrida",
        })
        results = self.vector_store.hybrid_search(
            question=question,
            query_embedding=query_embedding,
            k=settings.retrieval_top_k,
            candidate_k=settings.retrieval_candidate_k,
            where=metadata_filter,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        self.state.publish_query_event(query_id, {
            "status": "RERANKING",
            "progress": 55,
            "message": "Reordenando resultados por relevancia",
        })
        reranked_docs, reranked_meta = self.reranker.rerank(
            question=question,
            documents=documents,
            metadatas=metadatas,
            distances=distances,
            top_k=settings.retrieval_top_k,
        )
        context = "\n\n".join(reranked_docs)

        history = self.conversations.get_history(user_id=user_id, session_id=session_id)
        history_text = "\n".join(
            f"{turn.get('role', 'user')}: {turn.get('text', '')}"
            for turn in history[-5:]
        )

        self.state.publish_query_event(query_id, {
            "status": "PROMPT_BUILD",
            "progress": 70,
            "message": "Construyendo prompt con contexto e historial",
        })
        prompt = f"""
Responde usando solo el contexto proporcionado.
Si no hay suficiente información, dilo explícitamente.

Pregunta:
{question}

Historial reciente:
{history_text}

Contexto:
{context}
""".strip()

        self.state.publish_query_event(query_id, {
            "status": "GENERATING",
            "progress": 85,
            "message": f"Generando respuesta con {settings.llm_model}",
        })
        answer = self.llm.generate(prompt)
        self.conversations.add_turn(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            text=answer,
            sources=reranked_meta,
        )
        persistent_state = self.conversations.merge_persistent_context(
            user_id=user_id,
            context={
                "last_session_id": session_id,
                "last_question": question,
                "last_query_id": query_id,
            },
        )

        final_payload = {
            "status": "DONE",
            "progress": 100,
            "message": "Respuesta lista",
            "answer": answer,
            "sources": reranked_meta,
            "user_state": persistent_state,
        }
        self.state.publish_query_event(query_id, final_payload)

        return {
            "answer": answer,
            "sources": reranked_meta,
            "user_state": persistent_state,
        }
