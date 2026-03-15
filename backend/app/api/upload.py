from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.api import UploadAcceptedItem, UploadAcceptedResponse
from app.schemas.events import DocumentUploadedPayload, EventEnvelope
from app.services.document_registry import DocumentRegistryService
from app.services.file_storage import FileStorageService
from app.services.kafka_producer import KafkaProducerService
from app.services.redis_state import RedisStateService

router = APIRouter(prefix="/api", tags=["upload"])

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}


@router.post("/upload", response_model=UploadAcceptedResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
    document_ids: str | None = Form(default=None),
):
    if not files:
        raise HTTPException(status_code=400, detail="Debe enviar al menos un archivo.")

    provided_document_ids = []
    if document_ids:
        provided_document_ids = [item.strip() for item in document_ids.split(",") if item.strip()]
        if provided_document_ids and len(provided_document_ids) != len(files):
            raise HTTPException(
                status_code=400,
                detail="Si envía document_ids, debe haber uno por archivo.",
            )

    storage = FileStorageService()
    registry = DocumentRegistryService()
    redis_state = RedisStateService()
    producer = KafkaProducerService()

    batch_id = str(uuid4())
    accepted_items: list[UploadAcceptedItem] = []

    for index, file in enumerate(files):
        suffix = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.filename}")

        logical_document_id = provided_document_ids[index] if provided_document_ids else str(uuid4())
        _, path, content_hash = await storage.save_upload(file)
        file_version = registry.reserve_next_version(logical_document_id)
        registry.set_current_hash(logical_document_id, file_version, content_hash)
        correlation_id = str(uuid4())

        payload = DocumentUploadedPayload(
            batch_id=batch_id,
            document_id=logical_document_id,
            file_version=file_version,
            filename=file.filename,
            path=path,
            content_hash=content_hash,
            content_type=file.content_type,
        )

        event = EventEnvelope(
            event_type="document.uploaded",
            correlation_id=correlation_id,
            pipeline_version=settings.pipeline_version,
            payload=payload.model_dump(),
        )

        redis_state.set_document_status(
            logical_document_id,
            batch_id=batch_id,
            filename=file.filename,
            file_version=file_version,
            status="UPLOADED",
            progress=10,
            stage_message="Archivo recibido y enviado a la cola",
        )

        producer.publish(
            settings.kafka_topic_uploaded,
            event.model_dump(mode="json"),
            key=logical_document_id,
        )

        accepted_items.append(
            UploadAcceptedItem(
                filename=file.filename,
                document_id=logical_document_id,
                file_version=file_version,
                correlation_id=correlation_id,
                batch_id=batch_id,
                status="UPLOADED",
            )
        )

    return UploadAcceptedResponse(batch_id=batch_id, items=accepted_items)