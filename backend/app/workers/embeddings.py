from rag.vector.chroma_store import ChromaStore

vector_store = ChromaStore()

ids = [f"{document_id}_{i}" for i in range(len(chunks))]

metadata = [{"document_id": document_id} for _ in chunks]

vector_store.add_embeddings(
    ids,
    embeddings,
    chunks,
    metadata
)