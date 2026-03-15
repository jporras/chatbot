import json

from confluent_kafka import Consumer

from app.core.config import settings
from app.schemas.events import EventEnvelope
from app.services.embedding_service import EmbeddingService
from app.services.kafka_producer import KafkaProducerService
from app.services.redis_state import RedisStateService
from app.services.vector_store import VectorStoreService


def run() -> None:
    consumer = Consumer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "group.id": settings.kafka_group_embedding,
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe([settings.kafka_topic_chunked])

    producer = KafkaProducerService()
    redis_state = RedisStateService()
    embedder = EmbeddingService()
    vector_store = VectorStoreService()

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
        chunks = payload["chunks"]
        correlation_id = event["correlation_id"]

        try:
            redis_state.set_document_status(
                document_id,
                batch_id=batch_id,
                filename=filename,
                file_version=file_version,
                status="EMBEDDING",
                progress=80,
                stage_message=f"Generando embeddings de {len(chunks)} chunks",
            )

            texts = [chunk["text"] for chunk in chunks]
            ids = [chunk["chunk_id"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]

            embeddings = embedder.embed_documents(texts)
            vector_store.add_chunks(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            producer.publish(
                settings.kafka_topic_indexed,
                EventEnvelope(
                    event_type="document.indexed",
                    correlation_id=correlation_id,
                    pipeline_version=settings.pipeline_version,
                    payload={
                        "batch_id": batch_id,
                        "document_id": document_id,
                        "file_version": file_version,
                        "chunks_indexed": len(chunks),
                        "embedding_model": settings.rag_model,
                    },
                ).model_dump(mode="json"),
                key=document_id,
            )

            redis_state.set_document_status(
                document_id,
                batch_id=batch_id,
                filename=filename,
                file_version=file_version,
                status="INDEXED",
                progress=100,
                stage_message="Documento indexado correctamente",
            )

        except Exception as exc:
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
                        "stage": "embedding_worker",
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
                stage_message="Falló la generación de embeddings",
                error=str(exc),
            )
