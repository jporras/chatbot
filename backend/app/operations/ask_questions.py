class AskQuestion:

    def __init__(self, rag_service):
        self.rag_service = rag_service

    def execute(self, question: str) -> dict:

        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        answer = self.rag_service.generate_answer(question)

        return {
            "question": question,
            "answer": answer
        }