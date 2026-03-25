from app.api import documents


class FakeRedisState:
    def __init__(self) -> None:
        self._docs = {
            'doc-1': {
                'document_id': 'doc-1',
                'batch_id': 'batch-1',
                'filename': 'manual.pdf',
                'file_version': 1,
                'status': 'INDEXED',
                'progress': 100,
                'stage_message': 'Indexado',
                'updated_at': '2026-03-22T00:00:00+00:00',
                'error': None,
            }
        }

    def get_document_status(self, document_id: str):
        return self._docs.get(document_id)

    def get_batch_status(self, batch_id: str):
        if batch_id == 'batch-1':
            return [self._docs['doc-1']]
        return []


def test_get_document_status_ok(client, monkeypatch):
    monkeypatch.setattr(documents, 'RedisStateService', FakeRedisState)

    response = client.get('/api/documents/doc-1/status')

    assert response.status_code == 200
    assert response.json()['document_id'] == 'doc-1'


def test_get_document_status_not_found(client, monkeypatch):
    monkeypatch.setattr(documents, 'RedisStateService', FakeRedisState)

    response = client.get('/api/documents/missing/status')

    assert response.status_code == 404
    assert response.json()['detail'] == 'Document not found'


def test_get_batch_status(client, monkeypatch):
    monkeypatch.setattr(documents, 'RedisStateService', FakeRedisState)

    response = client.get('/api/uploads/batch-1/status')

    assert response.status_code == 200
    payload = response.json()
    assert payload['batch_id'] == 'batch-1'
    assert len(payload['items']) == 1
