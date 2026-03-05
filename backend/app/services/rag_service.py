class RAGService:

    def __init__(self, vector_store, embedding_service, llm_client):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.llm_client = llm_client

    def retrieve_context(self, question: str, k: int = 3) -> str:
        query_vector = self.embedding_service.embed([question])[0]
        results = self.vector_store.similarity_search(query_vector, k=k)

        return "\n".join([r["document"] for r in results])

    def generate_answer(self, question: str) -> str:

        context = self.retrieve_context(question)

        prompt = f"""
Responde usando únicamente la información del contexto.
Si no está en el contexto, di que no lo sabes.

Contexto:
{context}

Pregunta:
{question}
"""

        return self.llm_client.generate(prompt)