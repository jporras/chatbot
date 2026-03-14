class Ask:

    def __init__(self, rag):
        self.rag = rag

    def execute(self, question: str) -> dict:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        answer = self.rag.generate_answer(question)

        return {
            "question": question,
            "answer": answer
        }