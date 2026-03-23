import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from confluent_kafka import Consumer

from app.core.config import settings
from app.monitoring.metrics import (
    record_chunks_generated,
    record_pipeline_document,
    record_pipeline_failure,
    start_worker_metrics_server,
    track_pipeline_stage,
)
from app.rag.chunker import MarkdownChunker, SemanticChunker
from app.rag.loader import DocumentLoader
from app.schemas.events import EventEnvelope
from app.services.kafka_producer import KafkaProducerService
from app.services.redis_state import RedisStateService


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run() -> None:
    start_worker_metrics_server(settings.parser_metrics_port)
    consumer = Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_group_parser,
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe([settings.kafka_topic_uploaded])

    producer = KafkaProducerService()
    redis_state = RedisStateService()
    loader = DocumentLoader()
    markdown_chunker = MarkdownChunker(settings.chunk_size, settings.chunk_overlap)
    semantic_chunker = SemanticChunker(
        chunk_size=settings.semantic_chunk_size,
        overlap_min=settings.semantic_chunk_overlap_min,
        overlap_max=settings.semantic_chunk_overlap_max,
    )

    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue
        
        event = json.loads(msg.value().decode("utf-8"))
        payload = event["payload"]

        batch_id = payload["batch_id"]
        document_id = payload["document_id"]
        file_version = payload["file_version"]
        filename = payload["filename"]
        path = payload["path"]
        content_hash = payload["content_hash"]
        correlation_id = event["correlation_id"]
        document_type = Path(path).suffix.lower().lstrip(".") or "unknown"
        strategy = "markdown" if document_type == "md" else "semantic"

        try:
            redis_state.set_document_status(
                document_id,
                batch_id=batch_id,
                filename=filename,
                file_version=file_version,
                status="PARSING",
                progress=30,
                stage_message="Extrayendo texto del documento",
            )

            with track_pipeline_stage("parser", "load_document", document_type):
                loaded_parts = loader.load(path)
            suffix = Path(path).suffix.lower()

            chunks: list[dict] = []
            global_chunk_index = 0

            redis_state.set_document_status(
                document_id,
                batch_id=batch_id,
                filename=filename,
                file_version=file_version,
                status="CHUNKING",
                progress=50,
                stage_message="Generando chunks del documento",
            )

            with track_pipeline_stage("parser", "chunk_document", document_type):
                for part_index, part in enumerate(loaded_parts):
                    part_text = part["text"]
                    part_metadata = part.get("metadata", {})

                    if suffix == ".md":
                        split_parts = markdown_chunker.split(part_text)
                    else:
                        split_parts = semantic_chunker.split(part_text)

                    for local_chunk_index, chunk in enumerate(split_parts):
                        chunk_text = chunk["text"]
                        merged_metadata = {
                            "document_id": document_id,
                            "file_version": file_version,
                            "is_latest": True,
                            "filename": filename,
                            "source": path,
                            "content_hash": content_hash,
                            "chunk_hash": sha256_text(chunk_text),
                            "part_index": part_index,
                            "chunk_index": global_chunk_index,
                            "local_chunk_index": local_chunk_index,
                            "uploaded_at": datetime.now(timezone.utc).isoformat(),
                            "pipeline_version": settings.pipeline_version,
                            "rag_model": settings.rag_model,
                            **part_metadata,
                            **chunk.get("metadata", {}),
                        }
                        chunks.append(
                            {
                                "chunk_id": str(uuid4()),
                                "chunk_index": global_chunk_index,
                                "text": chunk_text,
                                "metadata": merged_metadata,
                            }
                        )
                        global_chunk_index += 1

            chunked_event = EventEnvelope(
                event_type="document.chunked",
                correlation_id=correlation_id,
                pipeline_version=settings.pipeline_version,
                payload={
                    "batch_id": batch_id,
                    "document_id": document_id,
                    "file_version": file_version,
                    "filename": filename,
                    "content_hash": content_hash,
                    "chunks": chunks,
                },
            )
            with track_pipeline_stage("parser", "publish_chunked_event", document_type):
                producer.publish(
                    settings.kafka_topic_chunked,
                    chunked_event.model_dump(mode="json"),
                    key=document_id,
                )

            redis_state.set_document_status(
                document_id,
                batch_id=batch_id,
                filename=filename,
                file_version=file_version,
                status="CHUNKED",
                progress=60,
                stage_message=f"Chunks listos: {len(chunks)}",
            )
            record_chunks_generated(strategy, document_type, len(chunks))
            record_pipeline_document("parser", "success", document_type)

        except Exception as exc:
            record_pipeline_failure("parser_worker")
            record_pipeline_document("parser", "failed", document_type)
            producer.publish(
                settings.kafka_topic_failed,
                EventEnvelope(
                    event_type="document.failed",
                    correlation_id=correlation_id,
                    pipeline_version=settings.pipeline_version,
                    payload={
                        "batch_id": batch_id,
                        "document_id": document_id,
                        "file_version": file_version,
                        "stage": "parser_worker",
                        "error": str(exc),
                    },
                ).model_dump(mode="json"),
                key=document_id,
            )
            redis_state.set_document_status(
                document_id,
                batch_id=batch_id,
                filename=filename,
                file_version=file_version,
                status="FAILED",
                progress=100,
                stage_message="Falló el parsing",
                error=str(exc),
            )

if __name__ == "__main__":
    run()
