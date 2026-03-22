from app.api import upload


class FakeFileStorageService:
    async def save_upload(self, file):
        return file.filename, f'/tmp/{file.filename}', 'hash-123'


class FakeDocumentRegistryService:
    def reserve_next_version(self, logical_document_id: str) -> int:
        return 1

    def set_current_hash(self, logical_document_id: str, file_version: int, content_hash: str) -> None:
        return None


class FakeRedisStateService:
    def set_document_status(self, *args, **kwargs) -> None:
        return None


class FakeKafkaProducerService:
    def publish(self, *args, **kwargs) -> None:
        return None


def patch_dependencies(monkeypatch):
    monkeypatch.setattr(upload, 'FileStorageService', FakeFileStorageService)
    monkeypatch.setattr(upload, 'DocumentRegistryService', FakeDocumentRegistryService)
    monkeypatch.setattr(upload, 'RedisStateService', FakeRedisStateService)
    monkeypatch.setattr(upload, 'KafkaProducerService', FakeKafkaProducerService)


def test_upload_accepts_pdf_and_returns_batch(client, monkeypatch):
    patch_dependencies(monkeypatch)

    response = client.post(
        '/api/upload',
        files=[('files', ('manual.pdf', b'fake-pdf-bytes', 'application/pdf'))],
        data={'document_ids': 'manual-empleados'},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['batch_id']
    assert payload['items'][0]['document_id'] == 'manual-empleados'
    assert payload['items'][0]['status'] == 'UPLOADED'


def test_upload_rejects_unsupported_extension(client, monkeypatch):
    patch_dependencies(monkeypatch)

    response = client.post(
        '/api/upload',
        files=[('files', ('malicioso.exe', b'not-allowed', 'application/octet-stream'))],
    )

    assert response.status_code == 400
    assert 'Unsupported file type' in response.json()['detail']
