class RAG:

    def __init__(self, vector, llm):
        self.vector = vector
        self.llm = llm

    def ask(self, question: str):
        docs = self.vector.similarity_search(question, k=3)
        context = "\n\n".join([doc["document"] for doc in docs])
        prompt = f"""
            Use the following context to answer the question.

            Context:
            {context}

            Question:
            {question}

            Answer:
            """

        answer = self.llm.generate(prompt)
        return {
            "answer": answer,
            "sources": docs
        }