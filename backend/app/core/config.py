from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "chatbot-rag"
    app_env: str = "dev"
    app_port: int = 8000
    pipeline_version: str = "v1"

    upload_dir: str = "uploads"

    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_uploaded: str = "document.uploaded"
    kafka_topic_chunked: str = "document.chunked"
    kafka_topic_indexed: str = "document.indexed"
    kafka_topic_failed: str = "document.failed"
    kafka_group_parser: str = "parser-worker"
    kafka_group_embedding: str = "embedding-worker"

    redis_url: str = "redis://redis:6379/0"

    chroma_host: str = "chromadb"
    chroma_port: int = 8000
    chroma_collection: str = "documents"

    hf_token: str = ""
    rag_model: str = "BAAI/bge-m3"
    llm_model: str = "gemma3:4b"
    ollama_url: str = "http://ollama:11434"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 5


settings = Settings()