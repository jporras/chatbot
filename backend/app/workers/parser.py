import json
from kafka import KafkaConsumer
from core.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_DOCUMENT_UPLOADED,
    TOPIC_CHUNKS_CREATED
)
from services.kafka_producer import send_event
from rag.loader import load_document
from rag.chunker import split_documents


consumer = KafkaConsumer(
    TOPIC_DOCUMENT_UPLOADED,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)


print("Parser worker running...")

for message in consumer:

    data = message.value

    document_id = data["document_id"]
    path = data["path"]

    documents = load_document(path)

    chunks = split_documents(documents)

    chunk_texts = [c.page_content for c in chunks]

    event = {
        "document_id": document_id,
        "chunks": chunk_texts
    }

    send_event(TOPIC_CHUNKS_CREATED, event)