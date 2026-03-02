import numpy as np
import faiss
import requests
from sentence_transformers import SentenceTransformer

VECTOR_PATH = "vector_store"

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(f"{VECTOR_PATH}/index.faiss")
chunks = np.load(f"{VECTOR_PATH}/chunks.npy", allow_pickle=True)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

def retrieve_context(question, k=3):
    query_embedding = model.encode([question])
    D, I = index.search(np.array(query_embedding), k=k)
    return "\n".join([chunks[i] for i in I[0]])

def generate_answer(question):
    context = retrieve_context(question)

    prompt = f"""
Responde usando únicamente la información del contexto.
Si no está en el contexto, di que no lo sabes.

Contexto:
{context}

Pregunta:
{question}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]
