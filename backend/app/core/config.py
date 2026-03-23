from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========================
    # APP
    # ========================
    app_name: str = "chatbot-rag"
    app_env: str = "dev"
    app_port: int = 8000
    pipeline_version: str = "v1"

    upload_dir: str = "/app/uploads"

    # ========================
    # KAFKA
    # ========================
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_uploaded: str = "document.uploaded"
    kafka_topic_chunked: str = "document.chunked"
    kafka_topic_indexed: str = "document.indexed"
    kafka_topic_failed: str = "document.failed"
    kafka_group_parser: str = "parser-worker"
    kafka_group_embedding: str = "embedding-worker"

    # ========================
    # REDIS
    # ========================
    redis_url: str = "redis://redis:6379/0"

    # ========================
    # CHROMA
    # ========================
    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection: str = "documents"

    # ========================
    # MODELOS
    # ========================
    hf_token: str | None = None
    rag_model: str = "BAAI/bge-m3"
    llm_model: str = "gemma3:4b"
    ollama_url: str = "http://ollama:11434"

    # ========================
    # RAG CONFIG
    # ========================
    chunk_size: int = 1000
    chunk_overlap: int = 200
    semantic_chunk_size: int = 1200
    semantic_chunk_overlap_min: int = 80
    semantic_chunk_overlap_max: int = 260
    retrieval_top_k: int = 5
    retrieval_candidate_k: int = 12
    conversation_history_limit: int = 20

    # ========================
    # VALIDACIONES / HELPERS
    # ========================
    @property
    def chroma_url(self) -> str:
        return f"http://{self.chroma_host}:{self.chroma_port}"

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()