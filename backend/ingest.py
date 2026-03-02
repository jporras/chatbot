import os
import numpy as np
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

DOCS_PATH = "docs"
VECTOR_PATH = "vector_store"
CHUNK_SIZE = 500

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_pdfs():
    texts = []
    for file in os.listdir(DOCS_PATH):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(DOCS_PATH, file))
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    texts.append(content)
    return texts

def chunk_text(texts):
    chunks = []
    for text in texts:
        for i in range(0, len(text), CHUNK_SIZE):
            chunks.append(text[i:i+CHUNK_SIZE])
    return chunks

def main():
    os.makedirs(VECTOR_PATH, exist_ok=True)

    texts = load_pdfs()
    chunks = chunk_text(texts)

    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    faiss.write_index(index, f"{VECTOR_PATH}/index.faiss")
    np.save(f"{VECTOR_PATH}/chunks.npy", chunks)

    print("Indexación completa.")

if __name__ == "__main__":
    main()
